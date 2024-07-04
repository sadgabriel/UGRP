from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import Map
class SpaceAIModule:
    def __init__(self, given_text) -> None:    
        ##########################
        ### INITIALIZAION PART ###
        ##########################

        # create llm with hello world.
        self.llm = ChatOpenAI()
        print("Space module LLM model created:", self.llm.model_name)
        self.test_list = [0, 0, 0, 0]

        # given text attribute
        self.given_text = given_text

        # Map attribute.
        self.map = Map.Map()

        return
    
    def put(self, name, ID):
        self.map.put(ID)

        return
    
    def initialize(self):
        self.map.random_place()
        self.map.print_map()

    def is_movable(self):
        ###################
        # is movable part #
        ###################

        is_movable_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             """
             Determine whether the given command is related to movement. If so, output 1. If not, output 0.

            input: The dragon flew towards the mountain. It landed near the mountain.
            outout: 1

            input: (Z) ran at the wolf.
            output: 1

            input: The white wolf is sleeping.
            output: 0

            input: {input}
            output: 
            """),
            ("user", "{input}")
        ])

        is_movable_chain = is_movable_prompt | self.llm
        chain_invoke_content = is_movable_chain.invoke({"input": self.given_text}).content

        result = int(chain_invoke_content)
        self.test_list[0] = result

        return result

    def who_move_where(self):
        #######################
        # who move where part #
        #######################
        who_move_where_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
            Summarize who moved to where in one sentence. The sentence should contain only one subject and only one object.

            input: The dragon flew towards the mountain. It landed near the mountain.
            outout: The dragon move to the mountain.

            input: (Z) ran at the wolf.
            output: (Z) move to the wolf.

            input: The white wolf cried. Then the black wolf shakes its body. The brave man did not panic. First, the brave man decided to subdue the white wolf. And he approaches the white wolf.
            output: the brave man move to the white wolf.

            input: {input}
            output: 
            """),
            ("user", "{input}")
        ])

        who_move_where_chain = who_move_where_prompt | self.llm

        if self.is_movable():
            result = who_move_where_chain.invoke({"input": self.given_text}).content
        else:
            raise Exception("This is not movable.")

        self.test_list[1] = result

        return result

    def express(self):
        ########################
        # A→B expression part. #
        ########################
        expression_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
            Print out an expression for input.

            input: (C) moved towards (A).
            output: C→A

            input: (A) moved close to (B).
            output: A→B

            input: {input}
            output: 
            """),
            ("user", "{input}")
        ])

        expression_chain = expression_prompt | self.llm 
        move_expression = expression_chain.invoke({"input": self.who_move_where()}).content

        #########################################
        # Subject and Object partitioning part. #
        #########################################
        subject = move_expression.split('→')
        object = subject[1]
        subject = subject[0]
        self.test_list[2] = move_expression
        
        return self.test_list
    
    def move_by_text(self):
        self.express()
        move_expression = self.test_list[2]
        sub = move_expression.split('→')
        obj = sub[1]
        sub = sub[0]

        sub = self.IDize(sub)
        obj = self.IDize(obj)
        self.test_list[3] = str(sub) + "→" + str(obj)

        self.map.move_around(sub, obj)

        return
    
    def IDize(self, noun, idcontainer):
        ###################################
        # dragon => (ID)1 IDization part. #
        ###################################
        IDization_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
            Print out an expression for input.

            input: The Red Wolf, {{blue wolf : 1, red wolf : 2, hero : 3, tree : 4}}
            output: 2

            input: the hunter john, {{john : 1, maria : 2, daria : 3}}
            output: 1

            input: (MARIA), {{john : 1, maria : 2, daria : 3}}
            output: 2

            input: {input}
            output: 
            """),
            ("user", "{input}")
        ])

        IDization_chain = IDization_prompt | self.llm 

        ID = int(IDization_chain.invoke(noun + ', ' + idcontainer.strize()).content)

        return ID

#############################
# Testing spacemodule part. #
#############################
if __name__ == '__main__':
    """(A) attacked (B) with an ax.
    Since the distance is far, (A) must first move.
    Okay. (A) moved close to (B) first. Then attacked with an axe.
    Fortunately, (A) successed to do that."""

    """(A) want to attack (B), but (A) can't do that right away because it's a long way off.
    So (A) decides to wait first.
    Then suddenly (C) began to move quickly.
    (C) had been approaching (A) before it react.
    (A) have been defenselessly beaten by (C) teeth."""

    input_text = """A black dragon flew up to a big rock. And the warrior hid."""

    spacemodule = SpaceAIModule(input_text)
    spacemodule.put('dragon', 1)
    spacemodule.put('warrior', 2)
    spacemodule.put('rock', 3)
    spacemodule.put('A', 4)
    spacemodule.put('B', 5)
    spacemodule.put('C', 6)
    spacemodule.put('wall', 7)
    spacemodule.put('wall', 8)
    spacemodule.put('wall', 9)
    spacemodule.put('wall', 10)
    spacemodule.put('wall', 11)
    spacemodule.put('wall', 12)
    spacemodule.put('wall', 13)
    spacemodule.put('wall', 14)

    spacemodule.initialize()
    spacemodule.move_by_text()
    print("is movable, who move where, expression:", spacemodule.test_list)
    spacemodule.map.print_map()

    spacemodule.map.attack_move(4, 5, 2, 2)
    spacemodule.map.print_map()
    spacemodule.map.attack_move(4, 5, 2, 2)
    spacemodule.map.print_map()
    spacemodule.map.attack_move(4, 5, 2, 2)
    spacemodule.map.print_map()