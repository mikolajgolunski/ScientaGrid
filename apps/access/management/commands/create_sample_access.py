from django.core.management.base import BaseCommand
from apps.access.models import AccessCondition, PricingPolicy
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service
from datetime import date


class Command(BaseCommand):
    help = 'Creates sample access conditions and pricing policies'

    def handle(self, *args, **options):
        # Get first infrastructure
        infra = Infrastructure.objects.first()
        if not infra:
            self.stdout.write(self.style.ERROR('No infrastructure found'))
            return

        # Get some equipment and services
        equipment = Equipment.objects.first()
        service = Service.objects.first()

        # Create Access Condition 1: Infrastructure-level open access
        ac1, created = AccessCondition.objects.get_or_create(
            infrastructure=infra,
            access_type='by_approval',
            defaults={
                'requires_booking': True,
                'min_booking_days': 7,
                'max_booking_days': 90,
                'requires_training': True,
                'training_duration_hours': 4,
                'requires_safety_certification': True,
                'is_active': True
            }
        )
        if created:
            ac1.set_current_language('en')
            ac1.name = 'Standard Academic Access'
            ac1.description = 'Standard access conditions for academic researchers'
            ac1.eligibility_criteria = 'Academic researchers from recognized institutions, PhD students with supervisor approval'
            ac1.application_process = 'Submit online application form with research proposal, wait for approval (typically 5-10 days)'
            ac1.required_documents = 'Research proposal, institutional affiliation proof, CV, safety training certificate'
            ac1.terms_and_conditions = 'Users must acknowledge the facility in publications, follow safety protocols, clean up after use'
            ac1.set_current_language('pl')
            ac1.name = 'Standardowy Dostęp Akademicki'
            ac1.description = 'Standardowe warunki dostępu dla badaczy akademickich'
            ac1.eligibility_criteria = 'Badacze akademiccy z uznanych instytucji, doktoranci z zatwierdzeniem promotora'
            ac1.application_process = 'Złóż formularz aplikacyjny online z propozycją badawczą, czekaj na zatwierdzenie (zwykle 5-10 dni)'
            ac1.required_documents = 'Propozycja badawcza, dowód afiliacji instytucjonalnej, CV, certyfikat szkolenia BHP'
            ac1.terms_and_conditions = 'Użytkownicy muszą uwzględnić obiekt w publikacjach, przestrzegać protokołów bezpieczeństwa, posprzątać po użyciu'
            ac1.save()
            self.stdout.write(self.style.SUCCESS('Created infrastructure access condition'))

        # Create Access Condition 2: Equipment-specific restricted access
        if equipment:
            ac2, created = AccessCondition.objects.get_or_create(
                equipment=equipment,
                access_type='restricted',
                defaults={
                    'requires_booking': True,
                    'min_booking_days': 14,
                    'max_booking_days': 60,
                    'requires_training': True,
                    'training_duration_hours': 8,
                    'requires_safety_certification': True,
                    'requires_nda': True,
                    'is_active': True
                }
            )
            if created:
                ac2.set_current_language('en')
                ac2.name = 'Advanced Equipment Access'
                ac2.description = 'Restricted access for specialized equipment requiring advanced training'
                ac2.eligibility_criteria = 'Experienced researchers only, must demonstrate prior experience with similar equipment'
                ac2.application_process = 'Submit detailed project proposal, undergo competency assessment, complete mandatory training'
                ac2.required_documents = 'Detailed project plan, equipment experience documentation, references, NDA signed'
                ac2.terms_and_conditions = 'Operator must be present during use, no unattended operation, mandatory safety protocols'
                ac2.set_current_language('pl')
                ac2.name = 'Dostęp do Zaawansowanego Sprzętu'
                ac2.description = 'Ograniczony dostęp do specjalistycznego sprzętu wymagającego zaawansowanego szkolenia'
                ac2.eligibility_criteria = 'Tylko doświadczeni badacze, muszą wykazać się doświadczeniem z podobnym sprzętem'
                ac2.application_process = 'Złóż szczegółową propozycję projektu, przejdź ocenę kompetencji, ukończ obowiązkowe szkolenie'
                ac2.required_documents = 'Szczegółowy plan projektu, dokumentacja doświadczenia ze sprzętem, referencje, podpisane NDA'
                ac2.terms_and_conditions = 'Operator musi być obecny podczas użytkowania, zakaz obsługi bez nadzoru, obowiązkowe protokoły bezpieczeństwa'
                ac2.save()
                self.stdout.write(self.style.SUCCESS('Created equipment access condition'))

        # Create Pricing Policy 1: Infrastructure general pricing
        pp1, created = PricingPolicy.objects.get_or_create(
            infrastructure=infra,
            pricing_type='per_hour',
            defaults={
                'base_price': 200.00,
                'academic_price': 100.00,
                'commercial_price': 500.00,
                'internal_price': 50.00,
                'includes_operator': True,
                'includes_analysis': False,
                'valid_from': date(2025, 1, 1),
                'is_active': True
            }
        )
        if created:
            pp1.set_current_language('en')
            pp1.name = 'Standard Hourly Rate'
            pp1.description = 'Standard pricing for facility access'
            pp1.price_notes = 'Discounts available for long-term projects (>100 hours). Additional charges for rush jobs.'
            pp1.set_current_language('pl')
            pp1.name = 'Standardowa Stawka Godzinowa'
            pp1.description = 'Standardowe ceny za dostęp do obiektu'
            pp1.price_notes = 'Zniżki dostępne dla projektów długoterminowych (>100 godzin). Dodatkowe opłaty za pilne zlecenia.'
            pp1.save()
            self.stdout.write(self.style.SUCCESS('Created infrastructure pricing'))

        # Create Pricing Policy 2: Service-specific pricing
        if service:
            pp2, created = PricingPolicy.objects.get_or_create(
                service=service,
                pricing_type='per_sample',
                defaults={
                    'base_price': 300.00,
                    'academic_price': 200.00,
                    'commercial_price': 800.00,
                    'internal_price': 100.00,
                    'setup_fee': 150.00,
                    'includes_operator': True,
                    'includes_analysis': True,
                    'valid_from': date(2025, 1, 1),
                    'is_active': True
                }
            )
            if created:
                pp2.set_current_language('en')
                pp2.name = 'Per Sample Analysis'
                pp2.description = 'Complete service including measurement and data analysis'
                pp2.price_notes = 'Bulk discounts: 10% off for 10+ samples, 20% off for 50+ samples. Setup fee waived for repeat customers.'
                pp2.set_current_language('pl')
                pp2.name = 'Analiza Pojedynczej Próbki'
                pp2.description = 'Kompletna usługa obejmująca pomiar i analizę danych'
                pp2.price_notes = 'Rabaty hurtowe: 10% zniżki dla 10+ próbek, 20% zniżki dla 50+ próbek. Opłata początkowa zniesiona dla stałych klientów.'
                pp2.save()
                self.stdout.write(self.style.SUCCESS('Created service pricing'))

        # Create Pricing Policy 3: Free academic access (equipment)
        if equipment:
            pp3, created = PricingPolicy.objects.get_or_create(
                equipment=equipment,
                pricing_type='free',
                defaults={
                    'base_price': 0.00,
                    'includes_operator': False,
                    'includes_analysis': False,
                    'valid_from': date(2025, 1, 1),
                    'valid_until': date(2025, 12, 31),
                    'is_active': True
                }
            )
            if created:
                pp3.set_current_language('en')
                pp3.name = 'Free Academic Access Program'
                pp3.description = 'Limited free access for qualifying academic projects'
                pp3.price_notes = 'Available only for collaborative projects with our institution. Limited to 20 hours per semester per project.'
                pp3.set_current_language('pl')
                pp3.name = 'Program Bezpłatnego Dostępu Akademickiego'
                pp3.description = 'Ograniczony bezpłatny dostęp dla kwalifikujących się projektów akademickich'
                pp3.price_notes = 'Dostępne tylko dla projektów współpracy z naszą instytucją. Ograniczone do 20 godzin na semestr na projekt.'
                pp3.save()
                self.stdout.write(self.style.SUCCESS('Created free access pricing'))

        self.stdout.write(self.style.SUCCESS('Sample access conditions and pricing setup complete!'))