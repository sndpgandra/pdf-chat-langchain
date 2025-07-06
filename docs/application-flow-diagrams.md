# PDF Chat Bot - Application Flow Diagrams

## Overview
This document contains comprehensive Mermaid diagrams illustrating the application flow, user interactions, and system behavior within the PDF Chat Bot.

## 1. Main Application Flow

```mermaid
flowchart TD
    A[Application Start] --> B[Initialize Streamlit]
    B --> C[Setup Logging]
    C --> D[Load Environment Variables]
    D --> E[Initialize Session State]
    E --> F[Create Components]
    
    F --> G{Auto-process Check}
    G -->|Existing Data Found| H[Load Existing Data]
    G -->|No Data| I[Check for PDF Files]
    
    I --> J{PDF Files Found?}
    J -->|Yes| K[Auto-process PDF]
    J -->|No| L[Wait for Upload]
    
    H --> M[Display UI]
    K --> N{Processing Success?}
    N -->|Yes| M
    N -->|No| O[Display Error]
    L --> M
    O --> M
    
    M --> P[Two-Tab Interface]
    P --> Q[Upload & Process Tab]
    P --> R[Chat Tab]
    
    Q --> S[Handle Upload]
    R --> T[Handle Chat]
    
    S --> U[Process PDF Flow]
    T --> V[Chat Processing Flow]
    
    %% Styling
    classDef startClass fill:#c8e6c9
    classDef processClass fill:#bbdefb
    classDef decisionClass fill:#fff3e0
    classDef uiClass fill:#f3e5f5
    classDef errorClass fill:#ffcdd2
    
    class A,M startClass
    class B,C,D,E,F,H,K,S,T processClass
    class G,J,N decisionClass
    class P,Q,R,U,V uiClass
    class I,L,O errorClass
```

## 2. User Interaction Flow

```mermaid
journey
    title PDF Chat Bot User Journey
    
    section Getting Started
      Open Application: 5: User
      View Interface: 4: User
      Read Instructions: 3: User
    
    section Document Upload
      Select Upload Tab: 5: User
      Choose PDF File: 4: User
      Click Process: 5: User
      Wait for Processing: 2: User
      See Success Message: 5: User
    
    section First Chat
      Switch to Chat Tab: 5: User
      Type First Question: 4: User
      Submit Query: 5: User
      Wait for Response: 3: User
      Read Answer: 5: User
      Check Sources: 4: User
    
    section Continued Usage
      Ask Follow-up: 5: User
      Explore Different Topics: 4: User
      Reference Page Numbers: 5: User
      Ask Complex Questions: 3: User
    
    section Session Management
      Upload New PDF: 4: User
      Clear Current Document: 3: User
      Start Fresh Session: 5: User
```

## 3. Streamlit Tab Navigation Flow

```mermaid
stateDiagram-v2
    [*] --> AppLoaded
    
    AppLoaded --> UploadTab : user_clicks_upload_tab
    AppLoaded --> ChatTab : user_clicks_chat_tab
    
    state UploadTab {
        [*] --> NoFileSelected
        NoFileSelected --> FileSelected : select_file
        FileSelected --> Processing : click_process
        Processing --> ProcessComplete : success
        Processing --> ProcessError : error
        ProcessComplete --> ReadyForChat
        ProcessError --> NoFileSelected : retry
        
        FileSelected --> NoFileSelected : clear_selection
        ProcessComplete --> Processing : upload_new_file
    }
    
    state ChatTab {
        [*] --> NotReady
        NotReady --> ChatReady : pdf_processed
        ChatReady --> QueryInput : user_types
        QueryInput --> WaitingResponse : submit_query
        WaitingResponse --> ShowResponse : response_received
        ShowResponse --> ChatReady : continue_chat
        
        ChatReady --> NotReady : pdf_cleared
        QueryInput --> ChatReady : cancel_query
    }
    
    UploadTab --> ChatTab : switch_tabs
    ChatTab --> UploadTab : switch_tabs
    
    ReadyForChat --> ChatReady : switch_to_chat
    
    note right of NotReady
        Shows: "Please upload 
        and process a PDF first"
    end note
    
    note right of ChatReady
        Shows: Chat interface
        with input field
    end note
```

## 4. PDF Processing Workflow

```mermaid
flowchart LR
    subgraph "Upload Phase"
        A[User Selects File] --> B[File Validation]
        B --> C{Valid PDF?}
        C -->|No| D[Show Error]
        C -->|Yes| E[Display File Info]
    end
    
    subgraph "Processing Phase"
        E --> F[User Clicks Process]
        F --> G[Initialize Progress Bar]
        G --> H[Step 1: Extract Text]
        H --> I[Update Progress 30%]
        I --> J[Step 2: Create Chunks]
        J --> K[Update Progress 50%]
        K --> L[Step 3: Generate Embeddings]
        L --> M[Update Progress 70%]
        M --> N[Step 4: Store in Database]
        N --> O[Update Progress 100%]
    end
    
    subgraph "Completion Phase"
        O --> P[Clear Progress Bar]
        P --> Q[Update Session State]
        Q --> R[Show Success Message]
        R --> S[Enable Chat Tab]
    end
    
    subgraph "Error Handling"
        H --> T{Extract OK?}
        J --> U{Chunk OK?}
        L --> V{Embed OK?}
        N --> W{Store OK?}
        
        T -->|No| X[Text Extraction Error]
        U -->|No| Y[Chunking Error]
        V -->|No| Z[Embedding Error]
        W -->|No| AA[Storage Error]
        
        X --> BB[Show Error Message]
        Y --> BB
        Z --> BB
        AA --> BB
        BB --> CC[Reset State]
    end
    
    %% Styling
    classDef uploadClass fill:#e3f2fd
    classDef processClass fill:#f3e5f5
    classDef completeClass fill:#e8f5e8
    classDef errorClass fill:#ffcdd2
    
    class A,B,C,D,E uploadClass
    class F,G,H,I,J,K,L,M,N,O processClass
    class P,Q,R,S completeClass
    class T,U,V,W,X,Y,Z,AA,BB,CC errorClass
```

## 5. Chat Interface Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant SS as Session State
    participant CE as Chat Engine
    participant VS as Vector Store
    participant LLM as Google Gemini
    
    Note over U,LLM: Chat Session Start
    
    U->>UI: Navigate to Chat Tab
    UI->>SS: Check processed state
    
    alt PDF Not Processed
        SS-->>UI: processed = False
        UI-->>U: Show "Upload PDF first" warning
    else PDF Processed
        SS-->>UI: processed = True
        UI-->>U: Show chat interface
        
        Note over U,LLM: Chat Interaction Loop
        
        loop Chat Conversation
            U->>UI: Type question
            U->>UI: Press Enter/Click Send
            
            UI->>SS: Add user message to history
            UI->>UI: Display user message
            UI->>UI: Show "Thinking..." spinner
            
            UI->>CE: generate_response(query)
            CE->>VS: similarity_search(query)
            VS-->>CE: relevant chunks + metadata
            CE->>LLM: invoke(prompt)
            LLM-->>CE: response
            CE-->>UI: response + sources
            
            UI->>SS: Add assistant message to history
            UI->>UI: Display assistant response
            UI->>UI: Display source citations
            UI->>UI: Hide spinner
            
            Note over U,UI: User can continue asking questions
        end
    end
```

## 6. Error Handling and User Feedback Flow

```mermaid
flowchart TD
    A[User Action] --> B[Try Operation]
    
    B --> C{Operation Result}
    C -->|Success| D[Continue Normal Flow]
    C -->|Error| E[Determine Error Type]
    
    E --> F{Error Category}
    F -->|File Error| G[File-related Issue]
    F -->|Memory Error| H[Memory Issue]
    F -->|API Error| I[External Service Issue]
    F -->|Processing Error| J[Internal Processing Issue]
    F -->|Network Error| K[Connectivity Issue]
    
    G --> L[Show File Error Message]
    H --> M[Show Memory Error Message]
    I --> N[Show API Error Message]
    J --> O[Show Processing Error Message]
    K --> P[Show Network Error Message]
    
    L --> Q[Suggest File Solutions]
    M --> R[Suggest Memory Solutions]
    N --> S[Suggest API Solutions]
    O --> T[Suggest Processing Solutions]
    P --> U[Suggest Network Solutions]
    
    Q --> V[Allow Retry]
    R --> W[Force Cleanup & Retry]
    S --> X[Wait & Retry]
    T --> Y[Reset & Retry]
    U --> Z[Check Connection & Retry]
    
    V --> AA[User Decision]
    W --> AA
    X --> AA
    Y --> AA
    Z --> AA
    
    AA --> BB{User Choice}
    BB -->|Retry| B
    BB -->|Cancel| CC[Return to Previous State]
    BB -->|Reset| DD[Reset Application]
    
    D --> EE[Update UI State]
    CC --> EE
    DD --> FF[Reload Application]
    
    %% Error Message Examples
    L -.-> L1["Invalid PDF format<br/>Please select a valid PDF file"]
    M -.-> M1["Memory limit exceeded<br/>Try a smaller file"]
    N -.-> N1["API service unavailable<br/>Please try again later"]
    O -.-> O1["Processing failed<br/>Please check the file"]
    P -.-> P1["No internet connection<br/>Check your network"]
    
    %% Styling
    classDef actionClass fill:#e3f2fd
    classDef decisionClass fill:#fff3e0
    classDef errorClass fill:#ffcdd2
    classDef solutionClass fill:#f3e5f5
    classDef successClass fill:#e8f5e8
    
    class A,B,D actionClass
    class C,F,BB decisionClass
    class E,G,H,I,J,K,L,M,N,O,P errorClass
    class Q,R,S,T,U,V,W,X,Y,Z solutionClass
    class EE,FF successClass
```

## 7. Session State Management Flow

```mermaid
flowchart TD
    subgraph "Session Initialization"
        A[App Start] --> B[Check Session State]
        B --> C{State Exists?}
        C -->|No| D[Initialize Default State]
        C -->|Yes| E[Load Existing State]
    end
    
    subgraph "State Variables"
        F[processed: Boolean]
        G[chat_history: List]
        H[processed_file: String]
        I[initialization_complete: Boolean]
    end
    
    subgraph "State Updates"
        J[PDF Upload] --> K[Set processed = False]
        K --> L[Clear chat_history]
        L --> M[Set processed_file = None]
        
        N[PDF Processing] --> O[Set processed = True]
        O --> P[Set processed_file = filename]
        
        Q[Chat Message] --> R[Append to chat_history]
        
        S[Clear PDF] --> T[Reset all states]
        T --> U[processed = False]
        U --> V[chat_history = []]
        V --> W[processed_file = None]
    end
    
    subgraph "State Persistence"
        X[UI Interactions] --> Y[Automatic State Save]
        Y --> Z[Session Storage]
        Z --> AA[State Available Next Interaction]
    end
    
    D --> F
    D --> G
    D --> H
    D --> I
    
    E --> F
    E --> G
    E --> H
    E --> I
    
    %% State flow connections
    J --> F
    N --> F
    Q --> G
    S --> F
    S --> G
    S --> H
    
    %% Persistence connections
    K --> X
    O --> X
    R --> X
    T --> X
    
    %% Styling
    classDef initClass fill:#e3f2fd
    classDef stateClass fill:#fff3e0
    classDef updateClass fill:#f3e5f5
    classDef persistClass fill:#e8f5e8
    
    class A,B,C,D,E initClass
    class F,G,H,I stateClass
    class J,K,L,M,N,O,P,Q,R,S,T,U,V,W updateClass
    class X,Y,Z,AA persistClass
```

## 8. Auto-Processing Logic Flow

```mermaid
flowchart TD
    A[App Initialization] --> B[Check initialization_complete]
    B --> C{First Load?}
    C -->|Yes| D[Start Auto-Process Logic]
    C -->|No| E[Skip Auto-Process]
    
    D --> F[Check Vector Store]
    F --> G{Existing Data?}
    G -->|Yes| H[Set processed = True]
    G -->|No| I[Check File System]
    
    H --> J[Load Existing State]
    J --> K[Display "Data Found" Message]
    
    I --> L[Scan data/uploads Directory]
    L --> M{PDF Files Found?}
    M -->|No| N[No Auto-Process]
    M -->|Yes| O[Select First PDF]
    
    O --> P[Check File Size]
    P --> Q{Size Acceptable?}
    Q -->|No| R[Skip Large File]
    Q -->|Yes| S[Start Processing]
    
    S --> T[Show Progress to User]
    T --> U[Process with Progress Updates]
    U --> V{Processing Success?}
    V -->|Yes| W[Set processed = True]
    V -->|No| X[Show Error Message]
    
    W --> Y[Update Session State]
    Y --> Z[Display Success Message]
    
    X --> AA[Log Error Details]
    AA --> AB[Reset State]
    
    R --> AC[Log Skip Reason]
    N --> AC
    AB --> AC
    
    K --> AD[Set initialization_complete = True]
    Z --> AD
    AC --> AD
    E --> AD
    
    AD --> AE[Continue to UI]
    
    %% Decision annotations
    G -.->|"Check document count > 0"| H
    M -.->|"glob('*.pdf')"| O
    Q -.->|"< 50MB recommended"| S
    
    %% Styling
    classDef startClass fill:#c8e6c9
    classDef checkClass fill:#fff3e0
    classDef processClass fill:#bbdefb
    classDef successClass fill:#e8f5e8
    classDef errorClass fill:#ffcdd2
    classDef endClass fill:#f3e5f5
    
    class A,D startClass
    class B,C,F,G,I,L,M,P,Q,V checkClass
    class S,T,U processClass
    class H,J,K,W,Y,Z successClass
    class R,X,AA,AB,AC errorClass
    class E,N,AD,AE endClass
```

## 9. Component Lifecycle Flow

```mermaid
stateDiagram-v2
    [*] --> ComponentInit
    
    state ComponentInit {
        [*] --> PDFProcessor
        PDFProcessor --> TextChunker
        TextChunker --> VectorStore
        VectorStore --> ChatEngine
        ChatEngine --> [*]
    }
    
    ComponentInit --> Ready
    
    state Ready {
        [*] --> Idle
        Idle --> Processing : pdf_upload
        Processing --> Idle : processing_complete
        
        Idle --> Chatting : user_query
        Chatting --> Idle : response_complete
        
        Processing --> Error : processing_error
        Chatting --> Error : chat_error
        Error --> Idle : error_resolved
    }
    
    Ready --> ComponentCleanup : session_end
    
    state ComponentCleanup {
        [*] --> Cleanup
        Cleanup --> ResourceRelease
        ResourceRelease --> [*]
    }
    
    ComponentCleanup --> [*]
    
    Ready --> ComponentInit : reset_components
    
    note right of ComponentInit
        Initialize:
        - PDF Processor
        - Text Chunker
        - Vector Store
        - Chat Engine
    end note
    
    note right of Processing
        Active operations:
        - Text extraction
        - Chunking
        - Embedding
        - Storage
    end note
    
    note right of Chatting
        Active operations:
        - Query processing
        - Vector search
        - LLM inference
        - Response formatting
    end note
```

## 10. Performance Monitoring Flow

```mermaid
graph TB
    subgraph "Monitoring Triggers"
        A[App Start] --> B[Memory Baseline]
        C[Before Processing] --> D[Memory Check]
        E[After Processing] --> F[Memory Check]
        G[Before Chat] --> H[Memory Check]
        I[After Chat] --> J[Memory Check]
    end
    
    subgraph "Memory Monitoring"
        B --> K[Log RSS/VMS]
        D --> K
        F --> K
        H --> K
        J --> K
        
        K --> L{Memory Usage OK?}
        L -->|Yes| M[Continue Operation]
        L -->|No| N[Memory Warning]
    end
    
    subgraph "Performance Metrics"
        O[Start Timer] --> P[Operation Execution]
        P --> Q[End Timer]
        Q --> R[Calculate Duration]
        R --> S[Log Performance]
    end
    
    subgraph "Resource Management"
        N --> T[Trigger Garbage Collection]
        T --> U[Force Cleanup]
        U --> V[Re-check Memory]
        V --> W{Memory Improved?}
        W -->|Yes| M
        W -->|No| X[Memory Error]
    end
    
    subgraph "Error Response"
        X --> Y[Log Critical Error]
        Y --> Z[Notify User]
        Z --> AA[Suggest Solutions]
        AA --> BB[Reset if Needed]
    end
    
    %% Performance monitoring connections
    C --> O
    E --> O
    G --> O
    I --> O
    
    P --> D
    P --> F
    P --> H
    P --> J
    
    %% Styling
    classDef monitorClass fill:#e3f2fd
    classDef performanceClass fill:#f3e5f5
    classDef resourceClass fill:#fff3e0
    classDef errorClass fill:#ffcdd2
    classDef successClass fill:#e8f5e8
    
    class A,B,C,D,E,F,G,H,I,J,K monitorClass
    class O,P,Q,R,S performanceClass
    class N,T,U,V,W resourceClass
    class X,Y,Z,AA,BB errorClass
    class L,M successClass
```

## 11. Complete User Workflow

```mermaid
journey
    title Complete PDF Chat Bot Workflow
    
    section Application Setup
      Start Application: 5: User
      Wait for Initialization: 2: User
      See Welcome Interface: 4: User
      Check Auto-processing: 3: System
    
    section Document Management
      Navigate to Upload Tab: 5: User
      Select PDF File: 4: User
      Review File Information: 3: User
      Initiate Processing: 5: User
      Monitor Progress: 2: User
      Confirm Success: 5: User
    
    section Initial Chat
      Switch to Chat Tab: 5: User
      Read Chat Instructions: 3: User
      Compose First Question: 4: User
      Submit Query: 5: User
      Wait for Processing: 2: User
      Review Answer: 5: User
      Check Source Citations: 4: User
    
    section Advanced Usage
      Ask Follow-up Questions: 5: User
      Explore Document Sections: 4: User
      Test Complex Queries: 3: User
      Verify Information: 4: User
      Use Page References: 5: User
    
    section Session Management
      Consider New Document: 3: User
      Clear Current Document: 4: User
      Upload Different PDF: 4: User
      Compare Information: 3: User
      End Session: 2: User
```

---

## Usage Instructions

### Rendering Diagrams
These Mermaid diagrams are best viewed in:
- GitHub repositories (native support)
- Mermaid Live Editor
- Documentation platforms with Mermaid support
- IDE extensions (VS Code, etc.)

### Diagram Categories
1. **Application Flow**: Overall system behavior
2. **User Interaction**: User journey and experience
3. **State Management**: Session and component states
4. **Error Handling**: Error flows and recovery
5. **Performance**: Monitoring and optimization

### Maintenance
Update these diagrams when:
- UI changes are implemented
- New features are added
- User workflows are modified
- Error handling is enhanced

---

*These application flow diagrams provide a comprehensive view of user interactions and system behavior within the PDF Chat Bot. They serve as both user experience documentation and development reference.*