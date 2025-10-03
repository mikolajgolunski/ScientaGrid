
# Research Infrastructure Database – Django Project

This Django project is designed to manage and explore research infrastructures, starting with Kraków and expanding to Poland and potentially other countries. It enables internal staff to catalog equipment, services, and access conditions, and to match infrastructures to specific research problems.

## 🧩 App Overview and Responsibilities

### 1. `infrastructures`
Handles core data about research infrastructures.

- Models: `Infrastructure`, `Institution`, `ContactPerson`, `AccessCondition`
- Stores metadata such as reliability, internal comments, and location
- Central entity linking equipment, services, and geographic data

### 2. `equipment`
Manages technical equipment and its capabilities.

- Models: `Equipment`, `Service`, `EquipmentService`
- Supports many-to-many relationships between equipment and services
- Enables filtering by technical specifications and service offerings

### 3. `research_problems`
Represents research needs and challenges.

- Models: `ResearchProblem`, `FieldOfScience`, `Keyword`
- Used to match infrastructures and services to research goals
- Supports classification and advanced filtering

### 4. `matching`
Encapsulates logic for matching infrastructures to research problems.

- Matching engine (rule-based or ML-ready)
- Scoring and recommendation logic
- Search and filtering interface

### 5. `locations`
Manages geographic and administrative data.

- Models: `City`, `Region`, `Country`
- Linked to infrastructures and institutions
- Supports geographic filtering and expansion beyond Kraków

### 6. `metadata`
Handles controlled vocabularies and multilingual labels.

- Models: `TechnologyDomain`, `InfrastructureCategory`, `LanguageLabel`
- Centralized classification system for filtering and internationalization

### 7. `users` *(optional)*
Manages internal staff and user profiles.

- Models: `UserProfile`, `Organization`
- Tracks who added or edited entries
- Supports role-based access and audit trails

## 🔄 App Interactions

- `Infrastructure` is the anchor entity, linking to `Institution`, `Location`, `ContactPerson`, and `AccessCondition`
- `Equipment` is hosted by `Infrastructure` and linked to `Service`
- `ResearchProblem` is matched to `Service` or `Equipment` via the `matching` app
- `metadata` provides classification and multilingual support across apps
- `locations` enables geographic filtering and expansion
- `users` tracks internal activity and permissions

## 🌐 Multilingual Support

The project supports Polish and English using Django’s internationalization features and model translation libraries.

## 🔐 Access Control

This system is intended for internal use only. No direct database access is provided to external clients.

---

This modular structure ensures scalability, maintainability, and clarity as the project grows across regions and research domains.
