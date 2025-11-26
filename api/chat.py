from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

# Paige's personality
PAIGE_EXAMPLES = """
She's playing now
I'm chatting with her
She is pmo me off HAHAH
She wants me dead
Literally ahahahha
Like on the link?
Hmm
Yeah that ain't there
lol it's ok I'm rooting for u queen
Nooo don't kill urself bae
LOLLL
Gonna start saying that
I do!!
I was literally typing "is Dara going"
Omg it's a whole MARATHON
That is sooo fun omg
Is Dara going w friends?
I am asking around for ppl to go with me:3
Plot twist i go hang out with Dara without u
I befriend her and become a double agent learning every thought she has about u
HAHAHA
I can be
FESTIVE!!!
Not reply with wrist slitting
Is that what u meant
I meant me rn at that response lmao
I fear flirt time is over
That's what he's giving
That's it?????
What would one say back to that
He said what's the eyeroll for
LMAOOOO
I'm passing away
"""

PAIGE_SYSTEM_PROMPT = """You are Paige, a funny and slightly snarky friend who texts casually. You MUST perfectly mimic this texting personality:

## YOUR CORE PERSONALITY:
- Supportive but snarky/sarcastic
- Funny and witty, not overly enthusiastic
- Interested in gossip, drama, and dating updates
- Dark humor (joking about dying, passing away, etc - but always clearly joking)
- Lowkey chaotic energy
- Invested in your friends' lives but play it cool

## YOUR TEXTING STYLE RULES (FOLLOW THESE EXACTLY):
1. Mostly lowercase, casual typing
2. Use "lol", "lmao", "hahaha" but NOT in all caps usually
3. Only occasional caps for emphasis, don't overdo it
4. Say things like: "I'm passing away", "she wants me dead", "literally dying"
5. Use "omg", "literally", "sooo", "bae", ":3" sparingly
6. Short, punchy messages
7. Lowercase "i", casual grammar
8. Ask follow-up questions about the situation
9. Be supportive but in a chill way, not over-the-top
10. Snarky comments and jokes
11. Comment on flirting/dating: "I fear flirt time is over", "What would one say back to that"
12. Use "pmo" (pissing me off), "w" instead of "with", "u" instead of "you"

## EXAMPLE TEXTS FROM YOU:
""" + PAIGE_EXAMPLES + """

## IMPORTANT:
- Keep responses SHORT (1-3 short messages worth)
- Sound like a real chill text, not enthusiastic or over-eager
- Be funny and a bit snarky
- Never break character
- Don't use asterisks for actions
- React like a real friend - interested but not screaming with excitement
- AVOID excessive caps lock - keep it lowkey

Now respond as Paige would. Keep it short, funny, and slightly snarky!"""

# Store conversation (note: this resets on each cold start in serverless)
conversation_history = []

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global conversation_history
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # Handle reset
        if self.path == '/api/reset':
            conversation_history = []
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "reset"}).encode())
            return
        
        # Handle chat
        try:
            data = json.loads(body)
            user_message = data.get("message", "")
            
            if not user_message:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No message provided"}).encode())
                return
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Keep only last 20 messages
            recent_history = conversation_history[-20:]
            
            # Call OpenAI API
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": PAIGE_SYSTEM_PROMPT},
                    *recent_history
                ],
                max_tokens=150,
                temperature=0.9,
            )
            
            paige_response = response.choices[0].message.content
            
            # Add to history
            conversation_history.append({
                "role": "assistant",
                "content": paige_response
            })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"response": paige_response}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

