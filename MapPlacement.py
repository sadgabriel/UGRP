from langchain_core.prompts import ChatPromptTemplate
class MapPlacement:
    def __init__(self):

        return
    
    def AI_place(self, description, matrix, idcontainer, llm):
        AI_place_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             """
             It is 30 feet per square of coordinate. Refer to the description and assign a coordinate to each object.

            input: Description: , (blue wolf : 1, red wolf : 2, hero : 3, tree : 4)
            output: {{blue wolf : (1,1)}}

            input: (Z) ran at the wolf.
            output: 1

            input: The white wolf is sleeping.
            output: 0

            input: {input}
            output: 
            """),
            ("user", "{input}")
        ])

        AI_place_chain = AI_place_prompt | llm
        chain_invoke_content = AI_place_chain.invoke({"input": self.given_text}).content

        result = int(chain_invoke_content)

        return