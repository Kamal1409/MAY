# MAY Project - Architecture Overview

## System Architecture

```mermaid
graph TB
    User[User Input] --> Parent[Parent Agent]
    Parent --> Child[Child Agent]
    Parent --> Resource[Resource Agent]
    
    Child --> LLM[LLM Backend]
    Parent --> LLM
    
    LLM --> KB[Knowledge Base]
    Scraper[Web Scraper] --> KB
    
    Child --> FileOps[File Operations]
    Child --> AppCtrl[App Control]
    Child --> SysMon[System Monitor]
    
    Resource --> Monitor[Resource Monitor]
    Resource --> Allocator[Resource Allocator]
    
    style Parent fill:#4CAF50
    style Child fill:#2196F3
    style Resource fill:#FF9800
    style LLM fill:#9C27B0
    style KB fill:#F44336
```

## Component Interactions

### 1. Child Agent → LLM → Actions
```mermaid
sequenceDiagram
    participant User
    participant Parent
    participant Child
    participant LLM
    participant System
    
    User->>Parent: Task Request
    Parent->>Child: Execute Task
    Child->>LLM: Get Action Plan
    LLM->>Child: Action Sequence
    Child->>System: Execute Actions
    System->>Child: Results
    Child->>Parent: Report Status
    Parent->>User: Final Result
```

### 2. Parent Agent Supervision
```mermaid
sequenceDiagram
    participant Child
    participant Parent
    participant LLM
    
    Child->>Parent: Action Request
    Parent->>Parent: Evaluate Safety
    alt Safe Action
        Parent->>Child: Approve
        Child->>System: Execute
    else Unsafe Action
        Parent->>Child: Reject
        Parent->>LLM: Refine Prompt
        LLM->>Parent: Better Prompt
        Parent->>Child: Retry with New Prompt
    end
```

### 3. Resource Management
```mermaid
sequenceDiagram
    participant Child
    participant Resource
    participant System
    
    Child->>Resource: Request Resources
    Resource->>System: Check Availability
    System->>Resource: Current Usage
    
    alt Resources Available
        Resource->>Child: Grant Access
    else Resources Limited
        Resource->>Child: Queue Request
        Resource->>Resource: Wait for Resources
        Resource->>Child: Grant When Available
    end
```

## Data Flow

### Knowledge Base Integration
```mermaid
graph LR
    Scraper[Web Scraper] -->|Raw Data| Processor[Data Processor]
    Processor -->|Cleaned Data| Embedder[Embedding Generator]
    Embedder -->|Vectors| VectorDB[(Vector Database)]
    
    Query[User Query] --> Embedder2[Query Embedder]
    Embedder2 --> VectorDB
    VectorDB -->|Relevant Docs| LLM[LLM]
    LLM -->|Enhanced Response| Agent[Agent]
```

## Agent Hierarchy

```mermaid
graph TD
    Parent[Parent Agent<br/>Supervisor & Refiner]
    
    Parent --> Child[Child Agent<br/>Task Executor]
    Parent --> Resource[Resource Agent<br/>System Monitor]
    
    Child --> FM[File Manager]
    Child --> AC[App Controller]
    Child --> SM[System Monitor]
    
    Resource --> RM[Resource Monitor]
    Resource --> RA[Resource Allocator]
    
    style Parent fill:#4CAF50,stroke:#2E7D32,stroke-width:3px
    style Child fill:#2196F3,stroke:#1565C0,stroke-width:2px
    style Resource fill:#FF9800,stroke:#E65100,stroke-width:2px
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.10+
- **Async Framework**: asyncio
- **Configuration**: Pydantic + YAML
- **Logging**: Loguru

### LLM Integration
- **Providers**: OpenAI, Anthropic
- **Framework**: LangChain
- **Function Calling**: Native API support

### Data & Storage
- **Vector Database**: ChromaDB
- **Embeddings**: sentence-transformers
- **Configuration**: YAML + .env

### System Operations
- **Process Management**: psutil
- **Automation**: pyautogui
- **Window Control**: pygetwindow

### Web Scraping
- **Static Content**: BeautifulSoup
- **Dynamic Content**: Playwright
- **HTTP Client**: httpx

## Security Model

### Safety Layers

1. **Path Validation**
   - Whitelist allowed directories
   - Blacklist system directories
   - Validate file extensions

2. **Permission Checks**
   - Verify user permissions
   - Check file/directory access
   - Validate operation type

3. **Resource Limits**
   - CPU usage caps
   - Memory allocation limits
   - Disk space checks
   - Network bandwidth limits

4. **Action Approval**
   - Parent agent oversight
   - User confirmation for critical actions
   - Audit logging

## Scalability Considerations

### Current Design (Phase 1-8)
- Single machine deployment
- Local LLM or API-based
- File-based configuration
- In-memory state management

### Future Enhancements
- Distributed agent deployment
- Centralized configuration service
- Database-backed state
- Load balancing
- Horizontal scaling

## Monitoring & Observability

### Metrics Collected
- Agent performance (success rate, latency)
- Resource utilization (CPU, memory, disk)
- LLM usage (tokens, cost, latency)
- Action execution (count, duration, errors)

### Logging Strategy
- Structured JSON logs
- Log levels per component
- Rotation and retention
- Centralized log aggregation (future)

## Error Handling

### Error Recovery Strategy
```mermaid
graph TD
    Error[Error Occurs] --> Classify{Error Type}
    
    Classify -->|Retryable| Retry[Retry with Backoff]
    Classify -->|Non-Retryable| Report[Report to Parent]
    
    Retry --> Success{Successful?}
    Success -->|Yes| Continue[Continue Execution]
    Success -->|No| MaxRetries{Max Retries?}
    
    MaxRetries -->|Yes| Report
    MaxRetries -->|No| Retry
    
    Report --> Parent[Parent Agent]
    Parent --> Refine[Refine Approach]
    Refine --> Retry2[Retry with New Strategy]
```

## Development Phases

| Phase | Component | Duration | Status |
|-------|-----------|----------|--------|
| 1 | Foundation & Setup | Week 1 | ✅ Complete |
| 2 | Child Agent | Week 2-3 | 🔄 Next |
| 3 | LLM Integration | Week 4-5 | ⏳ Pending |
| 4 | Parent Agent | Week 6-8 | ⏳ Pending |
| 5 | Resource Agent | Week 9-10 | ⏳ Pending |
| 6 | Web Scraping & KB | Week 11-12 | ⏳ Pending |
| 7 | Integration | Week 13-14 | ⏳ Pending |
| 8 | Documentation | Week 15-16 | ⏳ Pending |

---

**Last Updated**: November 29, 2025  
**Version**: 0.1.0  
**Status**: Phase 1 Complete
