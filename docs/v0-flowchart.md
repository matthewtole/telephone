```mermaid
flowchart TD
    idle -->|handset up| start
    interrupt --> |handset down| idle
    interrupt --> |911| emergency --> idle
    start --> play.intro
    play.intro --> intro.input
    intro.input -->|1| record.intro
    intro.input -->|2| message.random
    record.intro --> record.audio
    record.audio -->  record.after
    record.after --> play.intro
    message.random --> message.play
    message.play --> play.intro
```
