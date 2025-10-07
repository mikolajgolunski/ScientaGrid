from django.core.management.base import BaseCommand
from apps.research_problems.models import FieldOfScience, Keyword, ResearchProblem
from apps.infrastructures.models import Infrastructure


class Command(BaseCommand):
    help = 'Creates sample research problems and related data'

    def handle(self, *args, **options):
        # Create Fields of Science (based on OECD FOS)

        # Top-level fields
        natural_sciences, _ = FieldOfScience.objects.get_or_create(
            code='1',
            defaults={'is_active': True}
        )
        natural_sciences.set_current_language('en')
        natural_sciences.name = 'Natural Sciences'
        natural_sciences.description = 'Physical, chemical, earth and life sciences'
        natural_sciences.set_current_language('pl')
        natural_sciences.name = 'Nauki Przyrodnicze'
        natural_sciences.description = 'Nauki fizyczne, chemiczne, o Ziemi i życiu'
        natural_sciences.save()

        engineering, _ = FieldOfScience.objects.get_or_create(
            code='2',
            defaults={'is_active': True}
        )
        engineering.set_current_language('en')
        engineering.name = 'Engineering and Technology'
        engineering.description = 'Engineering, technology and applied sciences'
        engineering.set_current_language('pl')
        engineering.name = 'Inżynieria i Technologia'
        engineering.description = 'Inżynieria, technologia i nauki stosowane'
        engineering.save()

        medical, _ = FieldOfScience.objects.get_or_create(
            code='3',
            defaults={'is_active': True}
        )
        medical.set_current_language('en')
        medical.name = 'Medical and Health Sciences'
        medical.description = 'Medical and health-related sciences'
        medical.set_current_language('pl')
        medical.name = 'Nauki Medyczne i o Zdrowiu'
        medical.description = 'Nauki medyczne i związane ze zdrowiem'
        medical.save()

        # Sub-fields
        physics, _ = FieldOfScience.objects.get_or_create(
            code='1.3',
            defaults={'parent': natural_sciences, 'is_active': True}
        )
        physics.set_current_language('en')
        physics.name = 'Physical Sciences'
        physics.description = 'Physics and astronomy'
        physics.set_current_language('pl')
        physics.name = 'Nauki Fizyczne'
        physics.description = 'Fizyka i astronomia'
        physics.save()

        chemistry, _ = FieldOfScience.objects.get_or_create(
            code='1.4',
            defaults={'parent': natural_sciences, 'is_active': True}
        )
        chemistry.set_current_language('en')
        chemistry.name = 'Chemical Sciences'
        chemistry.description = 'Chemistry and related sciences'
        chemistry.set_current_language('pl')
        chemistry.name = 'Nauki Chemiczne'
        chemistry.description = 'Chemia i nauki pokrewne'
        chemistry.save()

        materials_eng, _ = FieldOfScience.objects.get_or_create(
            code='2.5',
            defaults={'parent': engineering, 'is_active': True}
        )
        materials_eng.set_current_language('en')
        materials_eng.name = 'Materials Engineering'
        materials_eng.description = 'Materials science and engineering'
        materials_eng.set_current_language('pl')
        materials_eng.name = 'Inżynieria Materiałowa'
        materials_eng.description = 'Nauka o materiałach i inżynieria'
        materials_eng.save()

        nanotechnology, _ = FieldOfScience.objects.get_or_create(
            code='2.10',
            defaults={'parent': engineering, 'is_active': True}
        )
        nanotechnology.set_current_language('en')
        nanotechnology.name = 'Nanotechnology'
        nanotechnology.description = 'Nanoscale science and technology'
        nanotechnology.set_current_language('pl')
        nanotechnology.name = 'Nanotechnologia'
        nanotechnology.description = 'Nauka i technologia w nanoskali'
        nanotechnology.save()

        self.stdout.write(self.style.SUCCESS('Created fields of science'))

        # Create Keywords
        keywords_data = [
            ('nanoparticles', 'Nanoparticles', physics),
            ('characterization', 'Characterization', chemistry),
            ('electron-microscopy', 'Electron Microscopy', physics),
            ('spectroscopy', 'Spectroscopy', chemistry),
            ('thin-films', 'Thin Films', materials_eng),
            ('surface-analysis', 'Surface Analysis', chemistry),
            ('drug-delivery', 'Drug Delivery', medical),
            ('biocompatibility', 'Biocompatibility', medical),
            ('crystal-structure', 'Crystal Structure', physics),
            ('polymers', 'Polymers', materials_eng),
        ]

        keyword_objs = {}
        for slug, name_en, field in keywords_data:
            kw, created = Keyword.objects.get_or_create(
                slug=slug,
                defaults={
                    'field_of_science': field,
                    'is_active': True
                }
            )
            if created:
                kw.set_current_language('en')
                kw.name = name_en
                kw.set_current_language('pl')
                kw.name = name_en  # Keep English for now
                kw.save()
            keyword_objs[slug] = kw

        self.stdout.write(self.style.SUCCESS(f'Created {len(keywords_data)} keywords'))

        # Create Research Problems

        # Problem 1: Nanoparticle characterization
        problem1, created = ResearchProblem.objects.get_or_create(
            submitted_by='Dr. Anna Kowalska, Jagiellonian University',
            contact_email='a.kowalska@example.com',
            defaults={
                'field_of_science': nanotechnology,
                'status': 'active',
                'priority': 'high',
                'complexity': 4,
                'estimated_budget': 5000.00,
                'estimated_duration_days': 30,
                'is_public': True
            }
        )
        if created:
            problem1.set_current_language('en')
            problem1.title = 'Characterization of Gold Nanoparticles for Drug Delivery'
            problem1.description = 'We need to characterize synthesized gold nanoparticles intended for targeted drug delivery applications. The particles are approximately 50-100 nm in diameter.'
            problem1.required_capabilities = 'TEM imaging for size and morphology, spectroscopy for surface properties, biocompatibility testing'
            problem1.expected_outcomes = 'High-resolution TEM images, particle size distribution, surface characterization data'
            problem1.constraints = 'Budget limited to 5000 PLN, need results within one month'
            problem1.set_current_language('pl')
            problem1.title = 'Charakteryzacja Nanocząstek Złota do Dostarczania Leków'
            problem1.description = 'Potrzebujemy charakteryzacji zsyntetyzowanych nanocząstek złota przeznaczonych do celowanego dostarczania leków. Cząstki mają średnicę około 50-100 nm.'
            problem1.required_capabilities = 'Obrazowanie TEM dla rozmiaru i morfologii, spektroskopia dla właściwości powierzchni, testy biokompatybilności'
            problem1.expected_outcomes = 'Obrazy TEM wysokiej rozdzielczości, rozkład wielkości cząstek, dane charakteryzacji powierzchni'
            problem1.constraints = 'Budżet ograniczony do 5000 PLN, potrzebne wyniki w ciągu miesiąca'
            problem1.save()
            problem1.keywords.add(
                keyword_objs['nanoparticles'],
                keyword_objs['characterization'],
                keyword_objs['electron-microscopy'],
                keyword_objs['drug-delivery']
            )
            problem1.additional_fields.add(physics, chemistry, medical)
            self.stdout.write(self.style.SUCCESS('Created nanoparticle problem'))

        # Problem 2: Thin film analysis
        problem2, created = ResearchProblem.objects.get_or_create(
            submitted_by='Prof. Jan Nowak, AGH University',
            contact_email='j.nowak@example.com',
            defaults={
                'field_of_science': materials_eng,
                'status': 'active',
                'priority': 'medium',
                'complexity': 3,
                'estimated_budget': 3000.00,
                'estimated_duration_days': 14,
                'is_public': True
            }
        )
        if created:
            problem2.set_current_language('en')
            problem2.title = 'Crystal Structure Analysis of Deposited Thin Films'
            problem2.description = 'Analysis of crystallographic structure and phase composition of thin films deposited by magnetron sputtering.'
            problem2.required_capabilities = 'X-ray diffraction (XRD) for phase identification, possibly TEM for microstructure'
            problem2.expected_outcomes = 'XRD patterns, phase identification, crystallite size estimation'
            problem2.constraints = 'Samples are sensitive to air exposure, need quick turnaround'
            problem2.set_current_language('pl')
            problem2.title = 'Analiza Struktury Krystalicznej Osadzonych Cienkich Warstw'
            problem2.description = 'Analiza struktury krystalograficznej i składu fazowego cienkich warstw osadzonych metodą rozpylania magnetronowego.'
            problem2.required_capabilities = 'Dyfrakcja rentgenowska (XRD) do identyfikacji faz, możliwe TEM dla mikrostruktury'
            problem2.expected_outcomes = 'Wzorce XRD, identyfikacja faz, oszacowanie rozmiaru krystalitów'
            problem2.constraints = 'Próbki są wrażliwe na ekspozycję powietrza, potrzebne szybkie wykonanie'
            problem2.save()
            problem2.keywords.add(
                keyword_objs['thin-films'],
                keyword_objs['crystal-structure'],
                keyword_objs['characterization']
            )
            problem2.additional_fields.add(physics)
            self.stdout.write(self.style.SUCCESS('Created thin film problem'))

        # Problem 3: Polymer characterization
        problem3, created = ResearchProblem.objects.get_or_create(
            submitted_by='Dr. Maria Wiśniewska, Research Institute',
            contact_email='m.wisniewska@example.com',
            defaults={
                'field_of_science': chemistry,
                'status': 'active',
                'priority': 'medium',
                'complexity': 2,
                'estimated_budget': 2000.00,
                'estimated_duration_days': 10,
                'is_public': False
            }
        )
        if created:
            problem3.set_current_language('en')
            problem3.title = 'UV-Vis Spectroscopy of Polymer Solutions'
            problem3.description = 'Need to analyze absorption spectra of various polymer solutions to determine concentration and purity.'
            problem3.required_capabilities = 'UV-Vis spectroscopy, sample preparation support'
            problem3.expected_outcomes = 'Absorption spectra, concentration data, purity assessment'
            problem3.constraints = 'Multiple samples (approx. 50), need automated measurement'
            problem3.set_current_language('pl')
            problem3.title = 'Spektroskopia UV-Vis Roztworów Polimerów'
            problem3.description = 'Potrzebujemy analizy widm absorpcji różnych roztworów polimerów w celu określenia stężenia i czystości.'
            problem3.required_capabilities = 'Spektroskopia UV-Vis, wsparcie w przygotowaniu próbek'
            problem3.expected_outcomes = 'Widma absorpcji, dane stężenia, ocena czystości'
            problem3.constraints = 'Wiele próbek (około 50), potrzebny automatyczny pomiar'
            problem3.save()
            problem3.keywords.add(
                keyword_objs['polymers'],
                keyword_objs['spectroscopy'],
                keyword_objs['characterization']
            )
            self.stdout.write(self.style.SUCCESS('Created polymer problem'))

        # Link problems to infrastructures
        infrastructures = Infrastructure.objects.all()
        if infrastructures.exists():
            infra = infrastructures.first()
            infra.research_problems.add(problem1, problem2)
            self.stdout.write(self.style.SUCCESS('Linked problems to infrastructure'))

        self.stdout.write(self.style.SUCCESS('Sample research problems setup complete!'))