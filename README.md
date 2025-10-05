# ScientaGrid – Research Infrastructure Database

ScientaGrid is a Django-based system designed to manage and explore research infrastructures, starting with Kraków and expanding to Poland and potentially other countries. It enables internal staff to catalog equipment, services, and access conditions, and to match infrastructures to specific research problems.

## 🧩 App Overview and Responsibilities

### Core Data Layer

#### 1. `institutions`
Manages organizations hosting infrastructures.

- Models: `Institution`
- Stores institutional metadata (name, type, website, etc.)
- Linked to infrastructures and locations
- Reusable across multiple infrastructures

#### 2. `locations`
Manages geographic and administrative data.

- Models: `Country`, `Region`, `City`
- Linked to infrastructures and institutions
- Supports geographic filtering and expansion beyond Kraków
- Hierarchical structure: Country → Region → City

#### 3. `infrastructures`
Handles core data about research infrastructures.

- Models: `Infrastructure`, `ContactPerson`
- Central entity linking equipment, services, institutions, and access conditions
- Stores metadata such as reliability, internal comments, and location
- Contact persons are stored here (no user accounts for them)

#### 4. `equipment`
Manages physical equipment and technical devices.

- Models: `Equipment`
- Linked to infrastructures
- Stores equipment metadata, status, and availability
- Connected to services and technical specifications

#### 5. `services`
Manages capabilities and services offered by equipment.

- Models: `Service`, `EquipmentService`
- Supports many-to-many relationships between equipment and services
- Same service can be offered by multiple equipment units
- Enables filtering by service offerings

#### 6. `access`
Handles access policies and conditions.

- Models: `AccessCondition`, `PricingPolicy`
- Defines who can use equipment/services and under what conditions
- Linked to infrastructures or specific equipment/services
- Includes pricing information
- Changes infrequently (typically annually)

### Classification Layer

#### 7. `research_problems`
Represents research needs and challenges.

- Models: `ResearchProblem`, `FieldOfScience`, `Keyword`
- Used to classify and connect infrastructures/services with research goals
- Provides basis for advanced filtering and matching
- Supports hierarchical field classification

#### 8. `taxonomy`
Handles controlled vocabularies and classifications.

- Models: `TechnologyDomain`, `InfrastructureCategory`, `Tag`
- Centralized classification system for filtering and categorization
- Manages controlled vocabularies across the system
- Supports standardized terminology

#### 9. `specifications`
Manages technical specifications and capabilities.

- Models: `Specification`, `SpecificationValue`
- Standardized technical parameters (resolution, temperature range, sample size, etc.)
- Enables structured technical filtering
- Linked to equipment for precise capability searching

### Feature Layer

#### 10. `search`
Handles advanced search and filtering across apps.

- Query logic for finding infrastructures, equipment, and services
- Interfaces with infrastructures, equipment, services, and research problems
- Filtering by location, specifications, availability, access conditions
- Provides search functionality for internal staff
- Future-ready for exposing API endpoints

#### 11. `matching` (Future Placeholder)
Encapsulates algorithms and rules for matching infrastructures to research problems.

- Recommendation engine (rule-based, ML-ready)
- Scoring and ranking logic
- Automated infrastructure-to-problem matching
- Does **not** include search UI; see `search`
- Currently a placeholder for future development

#### 12. `documents`
Manages file attachments and documentation.

- Models: `Document`, `DocumentType`
- Stores equipment manuals, safety protocols, photos, diagrams
- Linked to infrastructures, equipment, and services
- Includes metadata (upload date, file type, description)
- Supports categorization of document types

#### 13. `scheduling` (Future Placeholder)
Placeholder for equipment booking and scheduling.

- Models: `Booking`, `TimeSlot` (to be implemented)
- Equipment/service reservation system
- Availability calendar management
- Usage history tracking
- Integration with access policies
- Currently a placeholder for future development

### System Layer

#### 14. `users`
Manages internal staff accounts and profiles.

- Models: `UserProfile`, `StaffRole`
- Authentication and user management
- Role-based permissions for internal staff only
- User preferences and settings
- **Note:** Contact persons do NOT have accounts; they are stored in `infrastructures`

#### 15. `audit`
Tracks changes and maintains activity history.

- Models: `AuditLog`, `ChangeHistory`
- Records who added or edited entries
- Tracks all modifications to critical data
- Data quality metrics and completeness tracking
- Provides audit trails for accountability

#### 16. `api`
Provides integration endpoints for querying the system.

- Built on Django REST Framework
- Enables structured queries without direct database access
- Future-ready for external integrations
- Supports reporting and analytics tools
- Read-only access for data consumers

## 📊 App Hierarchy and Dependencies

```
Core Data Layer (institutions, locations, infrastructures, equipment, services, access)
    ↓
Classification Layer (research_problems, taxonomy, specifications)
    ↓
Feature Layer (search, matching*, documents, scheduling*)
    ↓
System Layer (users, audit, api)

* = Future placeholder
```

## 🔄 Key Data Relationships

- **Infrastructure** is the central entity, linking to:
  - `Institution` (host organization)
  - `Location` (geographic placement)
  - `ContactPerson` (points of contact, no user accounts)
  - `AccessCondition` (usage policies)
  - `Equipment` (hosted equipment)

- **Equipment** connects to:
  - `Infrastructure` (hosting location)
  - `Service` (many-to-many, what can be done)
  - `Specification` (technical capabilities)
  - `Document` (manuals, photos, protocols)

- **Service** links to:
  - `Equipment` (many-to-many, multiple equipment can offer same service)
  - `ResearchProblem` (via matching logic)

- **ResearchProblem** is classified by:
  - `FieldOfScience` (research domain)
  - `Keyword` (searchable terms)
  - Matched to services/equipment via `matching` app

- **Search** coordinates filtering across:
  - Infrastructures, equipment, services
  - Research problems
  - Locations, specifications, access conditions

- **Taxonomy** provides controlled vocabularies for:
  - All apps requiring standardized classification
  - Technology domains, categories, tags

- **Audit** tracks changes to:
  - All core data models
  - User actions and modifications

- **API** exposes structured queries for:
  - External reporting tools
  - Integration with other systems

## 🌍 Multilingual Support

The project supports **Polish and English** using:
- Django's built-in internationalization (`i18n`) framework
- `django-parler` for model field translations
- Translatable fields integrated directly into relevant models
- Translation files stored in standard Django `locale/` directories

**Implementation approach:**
- Core fields (names, descriptions) are translatable
- Technical specifications may remain in English for consistency
- UI labels and messages available in both languages

## 🔒 Access Control and Security

- **Internal use only**: No external user access to the database
- **Staff authentication**: Django's built-in authentication system
- **Role-based permissions**: Different access levels for staff members
- **Audit trails**: All changes tracked via `audit` app
- **Contact persons**: Stored as data only, no authentication

## 📈 Future Considerations

### Data Import (when needed)
- Bulk import functionality can be added as a management command or admin action
- CSV/Excel import for equipment and services
- Validation workflows can be implemented when multiple staff members collaborate

### Workflow States (when needed)
- Draft → Review → Published states
- Approval processes for sensitive data
- Data quality validation before publication

### Advanced Features (placeholders ready)
- **Matching app**: Recommendation algorithms for research problems
- **Scheduling app**: Equipment booking and reservation system
- These apps have defined structures but minimal implementation initially

## 🛠️ Technology Stack

- **Framework**: Django (Python)
- **Database**: MariaDB (utf8mb4 encoding)
- **API**: Django REST Framework
- **Translations**: django-parler
- **Admin**: Django Admin (customized for internal staff)

## 🚀 Development Approach

1. **Phase 1**: Core data layer - manually populate one record at a time
2. **Phase 2**: Classification and search functionality
3. **Phase 3**: API and audit trails
4. **Phase 4**: Advanced features (matching, scheduling, bulk import) as needed

---

This modular structure ensures scalability, maintainability, and clarity as the project grows across regions and research domains while remaining practical for current needs.
