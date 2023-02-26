# FINALES2 Interactions

To plan the hacking week a bit better here are some data flow diagrams for conceptualization.

# DATA FLOW
Here is a rough data and materials flow diagram without finales:

```mermaid
sequenceDiagram
INIT ->> OCond: fills preexisting values
INIT ->> OCyc: fills preexisting values
INIT ->> ORat: fills preexisting values

OCond ->> ASAB: New formulation for conductivity
OCond ->> ThreeDS: New formulation for conductivity

OCond ->> AB: New formulation for cell
AB ->> Cycler: Cells for cycling
Cycler ->> RULModel: Cycling Data
RULModel -->> Cycler: Early Stopping
Cycler ->> PARAModel: Cycling Data
PARAModel ->> DFNModel: Parameters
DB -->> ORat: Rate Capabilities
DFNModel -->> OCyc: Cycle Life
ASAB -->> OCond: Exp. Conductivity
ThreeDS -->> OCond: Sim. Conductivity
ASAB -->> OCyc: Exp. Conductivity
ThreeDS -->> OCyc: Sim. Conductivity
ASAB -->> ORat: Exp. Conductivity
ThreeDS -->> ORat: Sim. Conductivity
ASAB ->> DB: Exp Elyte Data
AB ->> DB: Manufacturing Data
Cycler ->> DB: Cycling Data
ThreeDS ->> DB: Sim Elyte Data
PARAModel ->> DB: DFN Parameters
OCond ->> DB: Model
OCyc ->> DB: Model
ORat ->> DB: Model
ORat -->> Cycler: High-fidelity tests
Cycler -->> ORat: High-fidelity data

DB ->> Archive: Nightly backup
```

# FINALES Functions

How everything interacts:

 
```mermaid
flowchart LR
    OCond[OCond]
    OCyc[OCyc]
    ORat[ORat]
    ASAB[ASAB]
    AB[AutoBASS]
    Cycler[Cycler]
    RULModel[RULModel]
    PARAModel[PARAModel]
    DFNModel[DFNModel]
    ThreeDS[3DSPipelinePilot]

    postRequest{{postRequest}}
    style postRequest fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    postData{{postData}}
    style postData fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    getRequest{{getRequest}}
    style getRequest fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    getData{{getData}}
    style getData fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    assembleXY{{assembleXY}}
    style assembleXY fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    triggerArchive{{triggerArchive}}
    style triggerArchive fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    registerTenant{{registerTenant}}
    style registerTenant fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    getCapability{{getCapability}}
    style getCapability fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    getLimitation{{getLimitation}}
    style getLimitation fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    setCapability{{setCapability}}
    style setCapability fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    setLimitation{{setLimitation}}
    style setLimitation fill:#bbf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    TEN-DB{TENANT DB}
    style TEN-DB fill:#faf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    RUN-DB{RUN DB}
    style RUN-DB fill:#faf,postRequest stroke-width:2px,stroke-dasharray: 5 5

    assembleXY --> getData
    registerTenant --> setCapability
    registerTenant --> setLimitation

    postData --> RUN-DB
    postRequest --> RUN-DB
    getRequest --> RUN-DB
    getData --> RUN-DB

    OCond --> assembleXY
    OCyc --> assembleXY
    ORat --> assembleXY

    RULModel ---> getData
    PARAModel ---> getData
    DFNModel ---> getData

    OCond --> postRequest
    OCyc --> postRequest
    ORat --> postRequest

    ASAB ---> getRequest
    Cycler ---> getRequest
    AB ---> getRequest
    ThreeDS ---> getRequest
    PARAModel ----> getRequest
    DFNModel ---> getRequest

    ASAB --> postData
    Cycler --> postData
    AB --> postData
    ThreeDS --> postData
    PARAModel --> postData
    DFNModel --> postData
    RULModel --> postData

    ASAB --> registerTenant
    AB --> registerTenant
    Cycler --> registerTenant
    RULModel --> registerTenant
    PARAModel --> registerTenant
    DFNModel --> registerTenant
    ThreeDS --> registerTenant

    OCyc ---> getLimitation
    ORat ---> getLimitation
    OCond ---> getLimitation

    OCyc ---> getCapability
    ORat ---> getCapability
    OCond ---> getCapability

    RUN-DB --> triggerArchive
    triggerArchive --> Archive

    TEN-DB --> triggerArchive

    setLimitation --> TEN-DB
    
    getLimitation --> TEN-DB
    setCapability --> TEN-DB
    getCapability --> TEN-DB
```
