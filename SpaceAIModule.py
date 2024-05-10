from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import SpaceAPIKey

##########################
### INITIALIZAION PART ###
##########################

# create llm with hello world.
llm = ChatOpenAI()
print(llm.model_name)

print("Hello World")

###################
# is movable part #
###################
"""(A) attacked (B) with an ax.
Since the distance is far, (A) must first move.
Okay. (A) moved close to (B) first. Then attacked with an axe.
Unfortunately, there was a trap in front of (B)."""

given_text = """(A) want to attack (B), but (A) can't do that right away because it's a long way off.
So (A) decides to wait first.
Then suddenly (C) began to move quickly.
(C) had been approaching (A) before it react.
(A) have been defenselessly beaten by (C) teeth."""


is_movable_prompt = ChatPromptTemplate.from_messages([
    ("system", "Determine whether the given command is related to movement. If so, output 1. If not, output 0."),
    ("user", "{input}")
])

is_movable_chain = is_movable_prompt | llm
chain_invoke_content = is_movable_chain.invoke({"input": given_text}).content

is_movable = int(chain_invoke_content)
print("is movable:", is_movable)

#######################
# who move where part #
#######################
who_move_where_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize who moved to where in one sentence. The sentence should contain only one subject and only one object."),
    ("user", "{input}")
])

who_move_where_chain = who_move_where_prompt | llm

if is_movable:
    who_move_where = who_move_where_chain.invoke({"input": given_text}).content
else:
    raise "This is not movable."

print("who move where:", who_move_where)

########################
# A→B expression part. #
########################
expression_prompt = ChatPromptTemplate.from_messages([
    ("system", "Give an article about movement. Summarize it in the expression like an example: \"A→B\". You must tell the expression only."),
    ("user", "{input}")
])

expression_chain = expression_prompt | llm 
move_expression = expression_chain.invoke({"input": who_move_where}).content
print("move expression:", move_expression)

#########################################
# Subject and Object partitioning part. #
#########################################
subject = move_expression.split('→')
object = subject[1]
subject = subject[0]
print("subject:", subject)
print("object:", object)

###############################
# Importing spacemodule part. #
###############################
import Map

map = Map.Map()
map.put('A')
map.put('B')
map.put('C')
map.random_place()

map.print_map()
map.move_around(subject, object)
print()
map.print_map()