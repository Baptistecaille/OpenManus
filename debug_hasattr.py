class Test:
    @property
    def client(self):
        return None


t = Test()
print(f"hasattr(t, 'client'): {hasattr(t, 'client')}")

from app.llm import LLM

l = LLM()
print(f"hasattr(l, 'client'): {hasattr(l, 'client')}")
print(f"l.client: {l.client}")
