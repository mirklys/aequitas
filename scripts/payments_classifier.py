import re
import unicodedata

class PaymentCategoryRBM:
    """This is a class for the rule-based model to categorize the transactions"""

    def __init__(self, data):
        self.categories = {
            'food': ['albert heijn', 'jumbo', 'lidl', 'spar', 'aldi', 'dirk', 'plus', 'coop', 'ah'],
            'travel': ['ns reizigers', 'swapfiets'],
            'stationary': ['bruna'],
            'suppliances': ['action', 'blokker', 'hema', 'ikea', 'media markt', 'coolblue', 'bol.com'],
            'eating out': ['mcdonalds', 'kfc', 'burger king', 'cafeteria', 'restaurant', 'cafe', 'café'],
            'friends': ['espinoza', 'espina'],
            'myself': ['giedrius', 'mirklys'],
            'insurance': ['vgz'],
            'rent': ['huur', 'real estate malden'],
            'subscription': ['spotify', 'google', 'subscriptions']
        }
        self.data = data

    def categorize(self):
        """This function categorizes the transactions based on the payment amount"""
        self.data['category'] = self.data['name'].apply(lambda x: self._assign_category(x))
        return self.data
    
    def _assign_category(self, name):
        """This function assigns the category to the transaction based on the name"""
        description = self._preprocess_text(name)
        
        for category, keywords in self.categories.items():
            pattern = '|'.join(re.escape(keyword) for keyword in keywords)
            
            if re.search(pattern, description):
                return category
        
        return "unknown"
    
    def _preprocess_text(self, text):
        text = unicodedata.normalize('NFKD', text)
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text