from datetime import datetime
import openai
import json
import os

openai.api_key = os.getenv("API_KEY")


def generate_natucal_english_sentence(context: str, original_english_text:str) -> str:
    """Get natual english sentence"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        functions=[{
            "name": "output_natural_english",
            "description": "You have to output natural english sentence. however, respect the original input.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "output_proofread_english_sentence": {
                        "type": "string",
                        "description": "you have to input natural english sentence",
                    }
                },
            }
        }],
        function_call={
            "name": "output_natural_english"
        },
        messages=[
            {"role": "user", "content": 
             f"Background: {context}. I am a non-native English speaker " + \
                f"so my English is bad. Please respect my context, and write a natural English sentence Please. rewrite these sentences: {original_english_text}"
            },
        ],

    )
    response_message = response["choices"][0]["message"]
    function_args = json.loads(response_message["function_call"]["arguments"])
    return function_args.get("output_proofread_english_sentence")

def proofread_english_sentence(context: str, original_english_text:str, natural_english_text: str) -> str:
    """Get natual english sentence"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        functions=[{
            "name": "output_correction_to_natural_english",
            "description": "You have to input the correction (proofread) result of english sentences. "+\
                            "If the range is correct or natural, you don't need to output it as arguments." +\
                            "If a range is almost of the sentence, specify the range as a whole sentence and rewrite it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start_word_position": {
                                    "type": "number",
                                    "description": "you have to specify the range to correct; output this item if only the range is bad unnatural expression: start word potision(index), 1-indexed.",
                                },
                                "end_word_position": {
                                    "type": "number",
                                    "description": "you have to specify the range to correct; output this item if only the range is bad unnatural expression:  end word potision(index), 1-indexed.",
                                },
                                "original_expression": {
                                    "type": "string"
                                },
                                "natural_expression": {
                                    "type": "string",
                                    "description": "you can replace the specified range to be these words or sentences."
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "the point the expression of the specified range is unnatural or why corrected"
                                }
                            },
                            "required": ["start_word_position", "end_word_position", "original_expression", "natural_expression", "reason"]
                        },
                    }
                }
            }
        }],
        function_call={
            "name": "output_correction_to_natural_english"
        },
        messages=[
            {"role": "user", "content": 
             f"Background: {context}. I am a non-native English speaker " + \
                f"so my English is bad. Please correct my English. Only output the unnatural range. " +\
                    f"If the range is almost all of a sentence, please specify the whole sentence. "+\
                        f" My text is this: `{original_english_text}`. " +\
                    f"You've already write natural sentences. this: `{natural_english_text}`. Please output the correction(proofread) result."
            },
        ],

    )
    response_message = response["choices"][0]["message"]


    function_args = json.loads(response_message["function_call"]["arguments"])
    print(f"function_args: {function_args}")
    return function_args


if __name__ == "__main__":
    # context = "I'm a student."
    # input_sentence = "hello, my namis Ryosuke. Today, I actidentaily  rebot a production instance at Yahoo! which I work for currently."
    context = "I want to ask a English question, for word definition."
    input_sentence = "Strategies and tactics are related but distinct concepts, often used in business, marketing, warfare, and other areas.A strategy is a high-level plan designed to achieve one or more long-term or overall goals under conditions of uncertainty. It's the big picture or the end goal, providing overall direction. For example, a company might have a growth strategy that includes expanding into new markets."
    print(f"context: {context}")
    print(f"input sentence: {input_sentence}")

    natural_sentence = generate_natucal_english_sentence(context=context, original_english_text=input_sentence)
    print(f"natural sentence: {natural_sentence}")


    proofread = proofread_english_sentence(context, original_english_text=input_sentence, natural_english_text=natural_sentence)    

    current_datetime = datetime.now()
    yy = current_datetime.strftime("%Y%m%d_%H%M%S")
    with open(f"output_correction_{yy}.json", "w") as f:
        json.dump(proofread, f)

