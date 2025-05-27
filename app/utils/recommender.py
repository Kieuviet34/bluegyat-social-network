class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
class UserNameTrie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word:str):
        node = self.root
        for ch in word.lower():
            node = node.children.setdefault(ch, TrieNode())
        node.is_word = True
    def _collect(self, node, prefix, results):
        if node.is_word:
            results.append(prefix)
        for ch, nxt in node.children.items():
            self._collect(nxt, prefix + ch, results)
    def suggest(self, prefix:str,max_suggest=5):
        node = self.root
        for ch in prefix.lower():
            node = node.children.get(ch)
            if node is None:
                return []
        results = []
        self._collect(node, prefix.lower(), results)
        return results[:max_suggest]