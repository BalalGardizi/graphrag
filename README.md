# graphrag

### Neo4Js DB and ingesting data 

`ingest_data.py` with llm and an entity embedder builds, entities, edges

![alt text](<pictures/Screenshot 2025-08-19 at 23.47.10.png>)

Data is ingested according to specific docoument types for scalability. 

Inside `data` we can dynamically change the facts. Graphiti automatically invalidates previous links, and updates the relationships, using LLM. We dont specify these changes explicitly. 

There is not any requirements to structure the data formating, expect it needs to be of the appropiate type indicated; json, text etc.

Its important to think about how to ingest data in terms of context. In case of `conversation.json` snippet of a chatbot and customer interacting. Send the entire, session, conversation as a single raw episode, for LLM to gain context within the episode. The id is specific to the unique conversation in order to seperate from other conversations. 

You can improve context by indicating the group_id, read here more: https://help.getzep.com/graphiti/core-concepts/graph-namespacing


 
### agent interaction

Build the graphiti client again, same as before in the `ingest_data.py`. It connects to the node.js db. You build a LLM agent to search in the space of the graph rag build by graphiti. This agent interacts with the customer. 

Here is an example where we change the contract type from basic to premium. 
![alt text](<pictures/Screenshot 2025-08-19 at 15.31.58.png>)

Interaction with the agent in live, without closig the application. 

![alt text](<pictures/Screenshot 2025-08-19 at 15.32.53.png>)
