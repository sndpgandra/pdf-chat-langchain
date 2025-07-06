# PDF Chat Bot - Data Flow Diagrams

## Overview
This document contains detailed Mermaid diagrams illustrating the data flow and processing pipelines within the PDF Chat Bot system.

## 1. Complete System Data Flow

```mermaid
graph TB
    subgraph "User Interface"
        A[User] --> B[Streamlit Web App]
        B --> A
    end
    
    subgraph "Document Processing Pipeline"
        C[PDF Upload] --> D[PDF Text Extraction]
        D --> E[Text Chunking]
        E --> F[Vector Embedding]
        F --> G[ChromaDB Storage]
    end
    
    subgraph "Query Processing Pipeline"
        H[User Query] --> I[Similarity Search]
        I --> J[Context Retrieval]
        J --> K[Prompt Engineering]
        K --> L[LLM Processing]
        L --> M[Response Generation]
        M --> N[Source Attribution]
    end
    
    subgraph "Data Storage"
        O[File System]
        P[ChromaDB]
        Q[Session State]
    end
    
    subgraph "External Services"
        R[Google Gemini API]
    end
    
    %% Connections
    B --> C
    C --> O
    D --> E
    E --> F
    F --> P
    G --> P
    
    B --> H
    I --> P
    J --> P
    K --> R
    L --> R
    R --> L
    M --> B
    N --> B
    
    B --> Q
    Q --> B
    
    %% Styling
    classDef userClass fill:#e1f5fe
    classDef processClass fill:#f3e5f5
    classDef storageClass fill:#e8f5e8
    classDef externalClass fill:#fff3e0
    
    class A,B userClass
    class C,D,E,F,G,H,I,J,K,L,M,N processClass
    class O,P,Q storageClass
    class R externalClass
```

## 2. Document Processing Flow

```mermaid
flowchart TD
    Start([Start: PDF Upload]) --> Upload[Upload PDF File]
    Upload --> Validate{Validate PDF}
    Validate -->|Invalid| Error1[Error: Invalid PDF]
    Validate -->|Valid| Extract[Extract Text from PDF]
    
    Extract --> Pages[Process Each Page]
    Pages --> Metadata[Add Page Metadata]
    Metadata --> Chunk[Create Text Chunks]
    
    Chunk --> ChunkConfig[Chunk Configuration:<br/>Size: 1000 chars<br/>Overlap: 200 chars]
    ChunkConfig --> Embed[Generate Vector Embeddings]
    
    Embed --> EmbedModel[Sentence Transformer:<br/>all-MiniLM-L6-v2]
    EmbedModel --> Store[Store in ChromaDB]
    
    Store --> Verify{Verify Storage}
    Verify -->|Success| Success[Processing Complete]
    Verify -->|Failure| Error2[Error: Storage Failed]
    
    Success --> Ready[Ready for Chat]
    Error1 --> End([End])
    Error2 --> End
    Ready --> End
    
    %% Styling
    classDef startEnd fill:#c8e6c9
    classDef process fill:#bbdefb
    classDef decision fill:#ffcdd2
    classDef error fill:#ffabab
    classDef config fill:#f8bbd9
    
    class Start,End,Ready startEnd
    class Upload,Extract,Pages,Metadata,Chunk,Embed,Store process
    class Validate,Verify decision
    class Error1,Error2 error
    class ChunkConfig,EmbedModel config
```

## 3. Vector Embedding Process

```mermaid
graph LR
    subgraph "Text Processing"
        A[Raw PDF Text] --> B[Text Cleaning]
        B --> C[Sentence Segmentation]
        C --> D[Text Chunks]
    end
    
    subgraph "Embedding Generation"
        D --> E[Sentence Transformer Model]
        E --> F[384-dim Vectors]
        F --> G[Vector Normalization]
    end
    
    subgraph "Storage Preparation"
        G --> H[Metadata Attachment]
        H --> I[Batch Formation]
        I --> J[ChromaDB Format]
    end
    
    subgraph "Database Operations"
        J --> K[ChromaDB Insert]
        K --> L[Index Creation]
        L --> M[Persistence]
    end
    
    %% Data flow annotations
    B -.->|"Remove special chars,<br/>normalize whitespace"| C
    D -.->|"1000 chars with<br/>200 char overlap"| E
    E -.->|"all-MiniLM-L6-v2<br/>model"| F
    H -.->|"Page numbers,<br/>document ID"| I
    I -.->|"Batch size: 25"| J
    
    %% Styling
    classDef textClass fill:#e3f2fd
    classDef embeddingClass fill:#f3e5f5
    classDef storageClass fill:#e8f5e8
    classDef dbClass fill:#fff3e0
    
    class A,B,C,D textClass
    class E,F,G embeddingClass
    class H,I,J storageClass
    class K,L,M dbClass
```

## 4. Query Processing and RAG Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Interface as Streamlit Interface
    participant ChatEngine as Chat Engine
    participant VectorStore as Vector Store
    participant ChromaDB as ChromaDB
    participant Gemini as Google Gemini
    
    User->>Interface: Submit Query
    Interface->>ChatEngine: generate_response(query)
    
    Note over ChatEngine: Step 1: Retrieve Context
    ChatEngine->>VectorStore: similarity_search(query)
    VectorStore->>ChromaDB: search with embedding
    ChromaDB-->>VectorStore: return top-k matches
    VectorStore-->>ChatEngine: relevant chunks + metadata
    
    Note over ChatEngine: Step 2: Prepare Context
    ChatEngine->>ChatEngine: format_context(chunks)
    ChatEngine->>ChatEngine: create_prompt(context, query)
    
    Note over ChatEngine: Step 3: Generate Response
    ChatEngine->>Gemini: invoke(prompt)
    Gemini-->>ChatEngine: generated response
    
    Note over ChatEngine: Step 4: Post-process
    ChatEngine->>ChatEngine: extract_sources(metadata)
    ChatEngine->>ChatEngine: format_response(response, sources)
    
    ChatEngine-->>Interface: response + sources
    Interface-->>User: display answer with citations
    
    Note over Interface: Update conversation history
    Interface->>Interface: update_session_state()
```

## 5. Similarity Search Process

```mermaid
graph TD
    A[User Query] --> B[Query Preprocessing]
    B --> C[Generate Query Embedding]
    C --> D[Vector Similarity Search]
    
    D --> E[ChromaDB Search]
    E --> F[Calculate Cosine Similarity]
    F --> G[Rank Results]
    G --> H[Filter by Threshold]
    
    H --> I[Extract Top-K Results]
    I --> J[Retrieve Document Text]
    J --> K[Retrieve Metadata]
    
    K --> L[Format Results]
    L --> M[Return to Chat Engine]
    
    subgraph "Search Parameters"
        N[k=5 documents]
        O[similarity threshold]
        P[distance metric: cosine]
    end
    
    subgraph "Result Format"
        Q[documents: List[str]]
        R[metadatas: List[Dict]]
        S[distances: List[float]]
    end
    
    %% Connections to parameters
    E --> N
    F --> O
    F --> P
    
    %% Connections to result format
    L --> Q
    L --> R
    L --> S
    
    %% Styling
    classDef queryClass fill:#e1f5fe
    classDef searchClass fill:#f3e5f5
    classDef resultClass fill:#e8f5e8
    classDef paramClass fill:#fff3e0
    
    class A,B,C queryClass
    class D,E,F,G,H,I searchClass
    class J,K,L,M resultClass
    class N,O,P,Q,R,S paramClass
```

## 6. Memory Management Flow

```mermaid
graph TB
    subgraph "Memory Monitoring"
        A[Start Process] --> B[Log Initial Memory]
        B --> C[Monitor RSS/VMS]
        C --> D[Check Memory Usage]
    end
    
    subgraph "Processing Stages"
        E[PDF Processing] --> F[Text Extraction]
        F --> G[Chunking]
        G --> H[Embedding]
        H --> I[Storage]
    end
    
    subgraph "Memory Management"
        J[Garbage Collection] --> K[Force GC]
        K --> L[Memory Cleanup]
        L --> M[Log Memory State]
    end
    
    subgraph "Batch Processing"
        N[Large Document] --> O[Split into Batches]
        O --> P[Process Batch]
        P --> Q[Memory Check]
        Q --> R{Memory OK?}
        R -->|Yes| S[Next Batch]
        R -->|No| T[Trigger Cleanup]
        T --> J
        S --> P
    end
    
    subgraph "Error Handling"
        U[Memory Error] --> V[Log Error]
        V --> W[Cleanup Resources]
        W --> X[User Notification]
    end
    
    %% Connections
    D --> E
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    
    N --> O
    Q --> D
    
    R --> U
    
    %% Styling
    classDef monitorClass fill:#e3f2fd
    classDef processClass fill:#f3e5f5
    classDef memoryClass fill:#e8f5e8
    classDef batchClass fill:#fff3e0
    classDef errorClass fill:#ffcdd2
    
    class A,B,C,D monitorClass
    class E,F,G,H,I processClass
    class J,K,L,M memoryClass
    class N,O,P,Q,R,S,T batchClass
    class U,V,W,X errorClass
```

## 7. Error Handling and Recovery Flow

```mermaid
graph TD
    A[Operation Start] --> B{Try Operation}
    B -->|Success| C[Continue Processing]
    B -->|Error| D[Catch Exception]
    
    D --> E{Error Type}
    E -->|Memory Error| F[Memory Cleanup]
    E -->|PDF Error| G[File Validation]
    E -->|API Error| H[API Retry Logic]
    E -->|DB Error| I[Database Recovery]
    E -->|Other Error| J[General Error Handler]
    
    F --> K[Log Memory State]
    G --> L[Log File Info]
    H --> M[Log API Response]
    I --> N[Log DB State]
    J --> O[Log Stack Trace]
    
    K --> P[User Notification]
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> Q[Cleanup Resources]
    Q --> R[Reset State]
    R --> S[End Process]
    
    C --> T[Success Path]
    T --> S
    
    %% Retry Logic
    H --> U{Retry Count < 3?}
    U -->|Yes| V[Wait and Retry]
    U -->|No| M
    V --> B
    
    %% Styling
    classDef startClass fill:#c8e6c9
    classDef decisionClass fill:#fff3e0
    classDef errorClass fill:#ffcdd2
    classDef handlerClass fill:#f3e5f5
    classDef logClass fill:#e3f2fd
    classDef endClass fill:#c8e6c9
    
    class A,T startClass
    class B,E,U decisionClass
    class D,F,G,H,I,J errorClass
    class K,L,M,N,O logClass
    class P,Q,R handlerClass
    class C,S endClass
```

## 8. Session State Management

```mermaid
stateDiagram-v2
    [*] --> Initialized
    
    Initialized --> PDFUploaded : upload_pdf()
    PDFUploaded --> Processing : process_pdf()
    Processing --> ProcessingComplete : success
    Processing --> ProcessingFailed : error
    
    ProcessingComplete --> ChatReady : initialize_chat()
    ProcessingFailed --> Initialized : reset()
    
    ChatReady --> ChatActive : send_query()
    ChatActive --> ChatReady : receive_response()
    
    ChatReady --> Initialized : clear_pdf()
    ChatActive --> Initialized : clear_pdf()
    
    ProcessingComplete --> Processing : upload_new_pdf()
    ChatReady --> Processing : upload_new_pdf()
    ChatActive --> Processing : upload_new_pdf()
    
    note right of Initialized
        - processed: False
        - chat_history: []
        - processed_file: None
    end note
    
    note right of ProcessingComplete
        - processed: True
        - processed_file: filename
        - vector_store: loaded
    end note
    
    note right of ChatReady
        - chat_engine: initialized
        - conversation_history: []
    end note
    
    note right of ChatActive
        - active_query: processing
        - response_pending: True
    end note
```

## 9. ChromaDB Data Structure

```mermaid
erDiagram
    COLLECTION {
        string name "pdf_documents"
        string embedding_function "all-MiniLM-L6-v2"
        datetime created_at
        datetime updated_at
    }
    
    DOCUMENT {
        string id "unique_identifier"
        text content "chunk_text"
        vector embedding "384_dim_vector"
        datetime created_at
    }
    
    METADATA {
        string document_id "references_document"
        integer page_number "source_page"
        string file_name "original_pdf"
        integer chunk_index "position_in_document"
        datetime processed_at
    }
    
    COLLECTION ||--o{ DOCUMENT : contains
    DOCUMENT ||--|| METADATA : has
    
    SEARCH_RESULT {
        string document_id
        float similarity_score
        float distance
        text content
        json metadata
    }
    
    DOCUMENT ||--o{ SEARCH_RESULT : generates
```

## 10. API Integration Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Config as Configuration
    participant Gemini as Google Gemini API
    participant Error as Error Handler
    
    App->>Config: load_dotenv()
    Config-->>App: environment variables
    
    App->>Config: validate_api_key()
    Config-->>App: API key validation
    
    App->>Gemini: initialize_client()
    Gemini-->>App: client instance
    
    loop For each query
        App->>Gemini: invoke(prompt)
        
        alt Successful Response
            Gemini-->>App: response object
            App->>App: extract_content()
            App->>App: format_response()
        
        else API Error
            Gemini-->>Error: error response
            Error->>Error: log_error()
            Error->>Error: check_retry_logic()
            
            alt Retry Available
                Error->>Gemini: retry_request()
            else Max Retries Reached
                Error-->>App: final error
                App->>App: handle_api_failure()
            end
        
        else Rate Limit
            Gemini-->>Error: rate limit error
            Error->>Error: exponential_backoff()
            Error->>Gemini: retry_after_delay()
        end
    end
    
    Note over App,Gemini: All API calls include proper error handling and logging
```

---

## Usage Notes

### Viewing Diagrams
These Mermaid diagrams can be viewed in:
- GitHub (native support)
- Mermaid Live Editor (https://mermaid.live)
- VS Code with Mermaid extension
- Any Markdown viewer with Mermaid support

### Customization
The diagrams can be customized by modifying:
- Colors and styling using CSS classes
- Node shapes and connections
- Layout direction and spacing
- Content and labels

### Updates
These diagrams should be updated when:
- System architecture changes
- New components are added
- Data flow is modified
- Error handling is updated

---

*These diagrams provide a comprehensive view of the data flow within the PDF Chat Bot system. They serve as both documentation and design reference for development and maintenance.*