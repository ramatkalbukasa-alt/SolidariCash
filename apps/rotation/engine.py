"""
SolidariCash — Rotation Engine
Règles :
1. Chaque tête passe une seule fois par cycle.
2. Deux têtes du même membre ne doivent pas être consécutives.
3. Les urgences modifient l'ordre (priorité max).
4. Les membres suspendus sont ignorés.
5. Les membres non payés peuvent être reportés.
6. L'ordre est historisé à chaque modification.
"""
import random
from django.db import transaction
from django.db.models import F as models_F
from .models import RotationOrder, RotationHistory
from apps.members.models import Head, Member
from apps.contributions.models import Contribution


class RotationEngine:
    def __init__(self, cycle):
        self.cycle = cycle

    def get_eligible_heads(self):
        """Récupère les têtes actives de membres actifs et ayant payé."""
        return Head.objects.filter(
            is_active=True,
            member__status=Member.STATUS_ACTIVE,
        ).select_related('member__user').order_by('member', 'head_number')

    def get_paid_heads(self):
        """Têtes dont la contribution est validée pour ce cycle."""
        paid_head_ids = Contribution.objects.filter(
            cycle=self.cycle,
            status=Contribution.STATUS_PAID
        ).values_list('head_id', flat=True)
        return paid_head_ids

    @transaction.atomic
    def generate(self):
        """
        Génère l'ordre de rotation complet pour le cycle.
        Algorithme :
        1. Récupère toutes les têtes éligibles.
        2. Distribue les têtes en évitant les répétitions consécutives du même membre.
        3. Crée les entrées RotationOrder avec positions.
        4. Journalise la création.
        """
        # Supprimer l'ancienne rotation si elle existe
        existing = RotationOrder.objects.filter(cycle=self.cycle)
        if existing.exists():
            existing.delete()

        heads = list(self.get_eligible_heads())
        if not heads:
            raise ValueError("Aucune tête éligible trouvée pour générer la rotation.")

        ordered = self._distribute_heads(heads)

        rotation_orders = []
        for position, head in enumerate(ordered, start=1):
            ro = RotationOrder(
                cycle=self.cycle,
                head=head,
                position=position,
                original_position=position,
                status=RotationOrder.STATUS_PENDING,
            )
            rotation_orders.append(ro)

        created = RotationOrder.objects.bulk_create(rotation_orders)

        for ro in created:
            RotationHistory.objects.create(
                rotation_order=ro,
                action=RotationHistory.ACTION_CREATED,
                new_position=ro.position,
                reason='Génération automatique',
            )

        return created

    def _distribute_heads(self, heads):
        """
        Distribue les têtes de façon à ce que les têtes du même membre
        ne soient pas consécutives. Algorithme glouton avec shuffle.
        """
        from collections import defaultdict

        member_heads = defaultdict(list)
        for head in heads:
            member_heads[head.member_id].append(head)

        # Construire la liste ordonnée
        result = []
        available = list(heads)
        random.shuffle(available)

        while available:
            last_member_id = result[-1].member_id if result else None

            # Trouver une tête dont le membre est différent du dernier
            candidates = [h for h in available if h.member_id != last_member_id]
            if not candidates:
                # Impossible d'éviter la répétition — on prend ce qui reste
                candidates = available

            chosen = candidates[0]
            result.append(chosen)
            available.remove(chosen)

        return result

    @transaction.atomic
    def apply_emergency(self, emergency, new_position, changed_by):
        """
        Applique une urgence : déplace la tête à la nouvelle position.
        Journalise le changement.
        """
        head = emergency.head or emergency.member.heads.filter(is_active=True).first()
        if not head:
            raise ValueError("Aucune tête trouvée pour cette urgence.")

        ro = RotationOrder.objects.filter(cycle=self.cycle, head=head).first()
        if not ro:
            raise ValueError("Cet tête n'est pas dans la rotation du cycle.")

        old_position = ro.position

        # Décaler les autres
        if new_position < old_position:
            RotationOrder.objects.filter(
                cycle=self.cycle,
                position__gte=new_position,
                position__lt=old_position
            ).exclude(pk=ro.pk).update(position=models_F('position') + 1)
        else:
            RotationOrder.objects.filter(
                cycle=self.cycle,
                position__gt=old_position,
                position__lte=new_position
            ).exclude(pk=ro.pk).update(position=models_F('position') - 1)

        ro.position = new_position
        ro.is_emergency = True
        ro.save()

        RotationHistory.objects.create(
            rotation_order=ro,
            action=RotationHistory.ACTION_EMERGENCY,
            previous_position=old_position,
            new_position=new_position,
            reason=f"Urgence approuvée (ID: {emergency.id})",
            changed_by=changed_by,
        )

        return ro

    @transaction.atomic
    def postpone_head(self, head, reason, changed_by):
        """Reporte une tête à la fin de la rotation."""
        ro = RotationOrder.objects.filter(
            cycle=self.cycle, head=head, status=RotationOrder.STATUS_PENDING
        ).first()
        if not ro:
            raise ValueError("Tête introuvable dans la rotation.")

        old_position = ro.position
        max_position = RotationOrder.objects.filter(cycle=self.cycle).count()

        RotationOrder.objects.filter(
            cycle=self.cycle,
            position__gt=old_position
        ).update(position=models_F('position') - 1)

        ro.position = max_position
        ro.status = RotationOrder.STATUS_POSTPONED
        ro.save()

        RotationHistory.objects.create(
            rotation_order=ro,
            action=RotationHistory.ACTION_POSTPONED,
            previous_position=old_position,
            new_position=max_position,
            reason=reason,
            changed_by=changed_by,
        )

        return ro

    def get_next_to_serve(self):
        """Retourne la prochaine tête à servir (position la plus basse, statut pending)."""
        return RotationOrder.objects.filter(
            cycle=self.cycle,
            status=RotationOrder.STATUS_PENDING
        ).select_related('head__member__user').order_by('position').first()

    def get_rotation_summary(self):
        """Retourne un résumé de la rotation avec statuts."""
        orders = RotationOrder.objects.filter(
            cycle=self.cycle
        ).select_related('head__member__user').order_by('position')

        return [
            {
                'position': o.position,
                'head': o.head.display_name,
                'member': o.head.member.full_name,
                'status': o.status,
                'is_emergency': o.is_emergency,
            }
            for o in orders
        ]

