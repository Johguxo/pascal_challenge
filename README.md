# **Pascal – Technical Coding Challenge**

### *Real Estate Conversational Agent over Telegram (Python)*

---

## **Context**

Pascal is building an AI-first operating system for real estate developers.

This challenge is a **small but realistic slice** of the technology behind our 24/7 AI conversational assistant.

It’s designed to be achievable but challenging enough to show your engineering mindset, code quality, and architectural thinking.

---

## **High-Level Goal**

Build a **Telegram conversational AI bot in Python** that can:

1. Receives free-form text messages in Spanish
2. Sends structured, formatted, helpful responses in Spanish
3. All secrets (Telegram token, DB creds, LLM keys) must come from environment variables.
4. Use an **orchestrator agent** to route each user message to the right agent.
    1. Handle an **onboarding / small-talk** experience.
    2. Search for real estate data using **PostgreSQL + RAG** (row-level embeddings).
    3. Allow users to **schedule a visit**, stored in an **appointments** table.

**You must use Python. Bonus points if you show your expertise with LangChain.**

Use of AI tools is allowed, but we will evaluate the cohesion, clarity, and intentionality of the codebase.

---

## **1. Agent Orchestrator & Agents**

Implement a lightweight **agent architecture** with:

### a. Orchestrator Agent

Classifies incoming messages into:

- `ONBOARDING_SMALL_TALK`
- `PROPERTY_SEARCH`
- `SCHEDULE_VISIT`

Then routes to the corresponding agent.

Classification can be done using an LLM prompt, simple heuristics, or LangChain agents.

### **b. Onboarding Agent**

Handles:

- Greetings (“Hola!”, “Buenas tardes.”)
- General questions (“Qué puedes hacer?”, "Quiero información.”)
- Light small talk

If the user already expresses intent (“Hola, estoy buscando un depa con 2 habitaciones”), it should naturally pass control to property search.

### **c. PropertySearch Agent**

Uses PostgreSQL + RAG to search:

- `projects`
- `properties`
- `typologies`

Returns a list of matching properties with key details like:

- project name
- property title
- bedrooms
- price
- district/city
- short description

### **d. Schedule Agent**

Handles: “Quiero agendar una visita”, “Puedo ir a visitarlos en Sábado?”.

The agent should:

1. Request missing information (if needed)
2. Insert an entry into an `appointments` table (schema below)
3. Send a simple confirmation message

---

## **2. PostgreSQL + RAG Requirements**

Feel free to create a PostgreSQL DB with the schemas below. You don’t need to deeply integrate every table into the flow, but they must be present and referenced where logical.

- **Leads**
    
    ```sql
    create table public.leads (
      id uuid not null default gen_random_uuid (),
      name text null,
      email text null,
      phone text null,
      created_at timestamp with time zone null default now(),
      updated_at timestamp with time zone null default now(),
      constraint leads_pkey primary key (id)
    );
    ```
    
- **Conversations**
    
    ```sql
    create table public.conversations (
      id uuid not null default gen_random_uuid (),
      most_recent_project_id uuid null,
      last_message_at timestamp with time zone null,
      is_answered_by_lead boolean null default false,
      lead_id uuid null,
      created_at timestamp with time zone null default now(),
      updated_at timestamp with time zone null default now(),
      constraint conversations_pkey primary key (id),
      constraint conversations_lead_id_fkey foreign KEY (lead_id) references leads (id) on update CASCADE on delete CASCADE,
      constraint conversations_most_recent_project_id_fkey foreign KEY (most_recent_project_id) references projects (id) on delete set null
    );
    ```
    
- **Messages**
    
    ```sql
    CREATE TYPE public.message_type AS ENUM (
      'human',
      'ai-assistant',
    );
    
    create table public.messages (
      id uuid not null default gen_random_uuid (),
      type public.message_type not null,
      content text not null,
      conversation_id uuid not null,
      constraint messages_pkey primary key (id),
      constraint messages_conversation_id_fkey foreign KEY (conversation_id) references conversations (id) on delete CASCADE
    );
    ```
    
- **Projects**
    
    ```sql
    create table public.projects (
      id uuid not null default gen_random_uuid (),
      name text null,
      description text null,
      district text null,
      address text null,
      reference text null,
      details text null,
      video_url text null,
      brochure_url text null,
      includes_parking boolean null default false,
      has_showroom boolean null default false,
      constraint projects_pkey primary key (id)
    );
    ```
    
- **Properties**
    
    ```sql
    create table public.properties (
      id uuid not null default gen_random_uuid (),
      title text null,
      type text null,
      description text null,
      pricing integer null,
      view_type text null,
      floor_no text null,
      project_id uuid null,
      typology_id integer null,
      constraint properties_pkey primary key (id),
      constraint fk_properties_project_id foreign KEY (project_id) references projects (id) on update CASCADE on delete set null,
      constraint properties_typology_id_fkey foreign KEY (typology_id) references typologies (id)
    );
    ```
    
- **Typologies**
    
    ```sql
    create table public.typologies (
      id uuid not null default gen_random_uuid (),
      name text null,
      description text null,
      type text null,
      num_bedrooms smallint null,
      num_bathrooms smallint null,
      area_m2 text null,
      constraint typologies_pkey primary key (id)
    );
    ```
    
- **Appointments**
    
    ```sql
    create table public.appointments (
      id uuid not null default gen_random_uuid (),
      lead_id uuid null,
      conversation_id uuid null,
      project_id uuid null,
      property_id uuid null,
      scheduled_for timestamptz null,
      created_at timestamp with time zone null default now(),
      constraint appointments_pkey primary key (id),
      constraint appointments_lead_id_fkey foreign key (lead_id) references leads (id),
      constraint appointments_conversation_id_fkey foreign key (conversation_id) references conversations (id),
      constraint appointments_project_id_fkey foreign key (project_id) references projects (id),
      constraint appointments_property_id_fkey foreign key (property_id) references properties (id)
    );
    ```
    

### **RAG Requirements**

- Use embedding column in all tables you think it's necessary (a good candidate is properties)
- Use any embedding model.
- Implement a simple vector similarity search using pgvector.
- Example signature:
    
    ```python
    # DB:
    alter table public.properties
    add column embedding vector(1536);
    
    # Python:
    def search_properties_with_rag(user_query: str, filters: dict | None = None):
        ...
    ```
    

---

## **3. Redis Cache**

Use Redis in two ways:

1. Conversation State Cache: ****Store last N (e.g., 5) recent messages for each user.

2. Property Search Cache: Cache search results using normalized query keys to avoid repeated embedding + DB calls.

---

## **4. Standard Reply Structure**

All responses should follow a structured JSON-like model, then converted to plain text for Telegram.

Example:

```json
{
  "type": "PROPERTY_SEARCH_RESULT",
  "summary": "Found 2 properties in Lima.",
  "items": [
    {
      "id": "prop_123",
      "project_name": "Edificio Ocean View",
      "title": "2BR Apartment",
      "price_usd": 120000,
      "district": "Miraflores"
    }
  ],
  "debug": {
    "decision": "PROPERTY_SEARCH",
    "source": "rag+db"
  }
}
```

We want to see a clean separation between: **internal structured logic (LLMs + business logic) +  presentation/formatting layer.**

---

## **5. Deliverables**

We look for **Head-of-Engineering-level quality**, even in a small project. We expect to see modular code, clean code, efficient calls (minimize redundant LLM + DB queries, caching) and design patterns.

You should deliver:

1. Git repository with the implementation of the code.
2. Detailed README (explain your architecture - we’re AI-driven, but we care that this reflects **your own thinking**).
3. Video Demo (max 10 min) showing Telegram conversation flow + key parts of your code.

---

## **6. Evaluation Criteria**

- Architecture & Design (20%)
- Code Quality (20%)
- Conversation Behavior & Functionality (30%)
    - Orchestrator routing behaves as expected.
    - RAG search returns reasonable properties.
    - Scheduling flow is usable end-to-end.
    - We’ll test:
        - **Greeting vs intent-rich greeting**
            - “Holaa!” → onboarding
            - “Hola, quisiera info de un depa con 3 habitaciones” → property search.
        - **Project-specific request**
            - “Dame información sobre el proyecto {project_name}”
        - **Follow-up questions without repeating the project**
            - “Cuál era el precio?”
            - “Qué pisos están disponibles?”
        - **Scheduling a visit**
            - “Quiero agendar una visita”, “Quisiera ir a visitarlos”.
            - Should store in `appointments` and confirm to the user.
- Use of Postgres, Redis, and RAG (25%)
- Documentation & Developer Experience (5%)