import pandas as pd
import NLP_Utils as NU
import geopy.distance
import pandas as pd
import numpy as np


def extractnum(line):    
    return ''.join([x for x in line if (x.isdigit())])

class ReceipeAnalyzer:    
    
    def __init__(self, homonyms = None, synonyms = None, stopwords = None):
        
        self.cal_to_J = 4.184
        self.J_to_cal = 1/4.184
        
        #food facts
        self.medianfacts = pd.read_parquet('medianfacts.parquet')
        self.allmedianfacts_subset = pd.read_parquet('allmedianfacts.parquet')
        
        #it would be better to create a class ProductMatcher and define its homonym/synonym dictionaries, and process them once
        self.homonyms = {'pomme':['pomme de terre'], 'poire':['poireau']}        
        self.synonyms = {'levure':['levain'],'lait':['boisson lactée'], 'patate':['pomme de terre']}
        self.stopwords = ['de','du','le','les','aux','la','des', 'a', 'une', 'un', 'au','g','gr','gramme','grammes','kg','kilo','kilos','kilogramme','kilogrammes','d','l']
        if homonyms is not None:
            self.homonyms = homonyms
        
        if synonyms is not None:
            self.synonyms = synonyms
        
        if stopwords is not None:
            self.stopwords = stopwords
        
        self.matcher = NU.SequenceMatcher(homonyms=self.homonyms,synonyms=self.synonyms, stopwords = self.stopwords)
        
        self.product_similarity = self.matcher.sequence_similarity
            
        self.verbosity = False
        
        self.warnings = True
    
    def empty_receipe():
        
        """
        valid ingredients: strings: e.g.: mydict['ingredients'] = ['tomates','spaghettis','boeuf haché']
        valid unit: 'u' (number of unit products) or 'g' (grams). E.g.: mydict['unit'] = ['u','g','g']
        valid qty: positive number. E.g.: mydict['qty'] = [4, 500, 400]
        """
        
        return {'ingredients':[],'unit':[],'qty':[]}
    
    def valeurs_nutritionnelles(self, query, quiet = None, th = 0.3, pretty = False):

        """
        query: string
        Note: ça dépend de nombreuses variables globales pour le moment!
        quiet: opposé de self.verbosity par défaut (si l'argument est laissé à None)
        """
        cal_to_J = 4.184
        J_to_cal = 1/cal_to_J

        medianfacts = self.medianfacts
        allmedianfacts_subset = self.allmedianfacts_subset
        stopwords = self.stopwords
        product_similarity = self.product_similarity
        
        queryst = NU.preprocess_string(query, stopwords)
        queryproduct = medianfacts[medianfacts.index == queryst]
        
        if quiet is None:
            quiet = not self.verbosity

        if len(queryproduct) == 0:    

            #rare product ?
            queryproduct = allmedianfacts_subset[allmedianfacts_subset.index == queryst]

            if len(queryproduct) > 0:
                if not quiet: print(query, "is an unusual product in the dataset")
            #else:
            if 0:

                #products starting with the query ?
                queryproduct = allmedianfacts_subset[allmedianfacts_subset.index.str.startswith(queryst)]
                if len(queryproduct) > 0:
                    if not quiet: print("no exact matching of", query, "in the dataset. Retrieved names starting by ", query)
                    qproducts = allmedianfacts_subset[allmedianfacts_subset.index.str.startswith(queryst)]
                    names = qproducts.product_name.to_list()
                    if len(names) > 0:
                        if not quiet: print(names)


        if len(queryproduct) == 0:
            if not quiet: print(query, "no match found in the dataset, getting most similar product name")

            #sims = medianfacts.product_name.apply(lambda x: similarity(x,query)).rename('sim')
            sims = medianfacts.product_name.apply(lambda x: product_similarity(x,query)).rename('sim')
            max_sim_idx = sims.idxmax()
            #print('max_sim:', max_sim_idx, sims[max_sim_idx])

            if sims[max_sim_idx] > th:
                queryproduct = medianfacts.loc[[max_sim_idx]]

            if len(queryproduct) == 0:
                if not quiet: print(query, "no match found in the usual dataset, getting most similar product name")

                #sims = allmedianfacts_subset.product_name.apply(lambda x: similarity(x,query)).rename('sim')
                sims = allmedianfacts_subset.product_name.apply(lambda x: product_similarity(x,query)).rename('sim')
                max_sim_idx = sims.idxmax()
                #print('max_sim:', max_sim_idx, sims[max_sim_idx])

                if sims[max_sim_idx] > th:
                    queryproduct = allmedianfacts_subset.loc[[max_sim_idx]]

        
        if len(queryproduct) > 0:        
            if not quiet: 
              print(query)
              print('(one of the numerous) product name:', queryproduct.product_name[0])
              print('kCal/100g:', queryproduct.energy_100g[0]*self.J_to_cal)
              print('fiber/100g:', queryproduct.fiber_100g[0])
              print('fat/100g:', queryproduct.fat_100g[0])
              print('saturated-fat/100g:', queryproduct['saturated-fat_100g'][0])
              print('carbohydrates/100g:', queryproduct.carbohydrates_100g[0])
              print('sugar/100g:', queryproduct.sugars_100g[0])
              print('protein/100g:', queryproduct.proteins_100g[0])
              print('salt/100g:', queryproduct.salt_100g[0])
              print('sodium/100g:', queryproduct.sodium_100g[0])
              print('additives:', queryproduct.additives_n[0])
              print('ingredients from palm oil:', queryproduct.ingredients_from_palm_oil_n[0])
              print('ingredients maybe from palm oil:', queryproduct.ingredients_that_may_be_from_palm_oil_n[0])

              print('nutrition score:', queryproduct['nutrition-score-fr_100g'][0])
              print('nutrition grade:', queryproduct['nutriscore_grade'][0])
              print('nova score:', queryproduct['nova_group'][0])
              if 'unit_weight_estimate' in queryproduct.columns:
                print('unit weight estimate (median):', queryproduct['unit_weight_estimate'][0])
              if 'unit_weight_estimate2' in queryproduct.columns:
                print('unit weight estimate 2 (most probable value):', queryproduct['unit_weight_estimate2'][0])
                

        if not quiet: print('\n')

        if pretty:
            queryproduct.insert(1, 'kCal/100g', queryproduct.energy_100g*self.J_to_cal, True)
            if 'unit_weight_estimate' in queryproduct.columns:
              queryproduct = queryproduct[['product_name','kCal/100g','fiber_100g','fat_100g', 'saturated-fat_100g', 'sugars_100g', 'proteins_100g', 'salt_100g' , 'sodium_100g', 'additives_n', 'ingredients_from_palm_oil_n', 'ingredients_that_may_be_from_palm_oil_n', 'nutrition-score-fr_100g', 'nova_group', 'unit_weight_estimate']]
              queryproduct.columns = ['Nom','kCal/100g','Fibres/100g','Graisses/100g','Gaisses saturées/100g','Sucre/100g','Protéines/100g','Sel/100g','Sodium/100g',"Additifs", "Ingrédients dérivés de l'huile de palme", "Ingrédients potentiellement dérivés de l'huile de palme", "Nutriscore","Nova-group", 'Weight (estimated)']
            else:
              queryproduct = queryproduct[['product_name','kCal/100g','fiber_100g','fat_100g', 'saturated-fat_100g', 'sugars_100g', 'proteins_100g', 'salt_100g' , 'sodium_100g', 'additives_n', 'ingredients_from_palm_oil_n', 'ingredients_that_may_be_from_palm_oil_n', 'nutrition-score-fr_100g', 'nova_group']]
              queryproduct.columns = ['Nom','kCal/100g','Fibres/100g','Graisses/100g','Gaisses saturées/100g','Sucre/100g','Protéines/100g','Sel/100g','Sodium/100g',"Additifs", "Ingrédients dérivés de l'huile de palme", "Ingrédients potentiellement dérivés de l'huile de palme", "Nutriscore","Nova-group"]
            queryproduct = queryproduct.transpose()
            queryproduct.columns.name = "Produit"
        return queryproduct    
           
    def units_to_grams(self, recette, nb_pers = None, no_delay = False):
        
        """
        
        """
        
        if nb_pers is None:
            Warning("Vous n'avez pas spécifié pour combien de personnes est la recette. Une valeur par défaut de 1 personne sera utilisée. Pour éviter cet avertissement, définissez l'attibut 'warnings' de cette clase à False, ou spécifiez un nombre de personnes")
            nb_pers = 1
        
        if type(recette) is dict:
            recettedf = pd.DataFrame(recette)
        elif type(recette) is pd.core.frame.DataFrame:
            recettedf = recette.copy()
        else:
            raise Exception("'recette' doit être soit de type dict, soit pandas.core.frame.DataFrame")
        
        #Pour les ingrédients donnés à l'unité, estimer le poids unitaire standard
        uindexes = recettedf.unit == 'u'
        queryingr = list(recettedf.ingredients[uindexes])        
        recettedf.index = recettedf.ingredients
        
        if len(queryingr) > 0:
        
            weights = []
            
            for q in queryingr:
                
                w = np.nan
                #extract unit weights from dataset
                if q in self.medianfacts.product_name:
                    w = self.medianfacts.loc[q].unit_weight_estimate
                    
                #query unit weight if not in dataset
                if np.isnan(w):
                    
                    out = NU.query_food_weight(q, no_delay = no_delay)
                    
                    if len(out) == 0:
                        print("unit_to_grams: no weight found, conversion cannot be performed.")
                        return recettedf
                        
                    #garder la valeur la plus probable
                    w = out[-4]
                
                weights.append(w)
                
            
            nbs = list(recettedf.loc[queryingr,'qty'])

            try:
                nbs = [float(n) for n in nbs]
            except:
                raise Exception("Veuillez entrer des quantités valides")

            weights = [w*n for w, n in zip(weights,nbs)]

            recettedf.loc[queryingr,'qty'] = weights

        recettedf.unit = 'g'

        recettedf.qty = recettedf.qty/nb_pers        
        
        return recettedf
    
    def compute_receipe(self, recette, nb_pers = None):
        
        if recette is None:
            return None
        
        try:
            recette.qty = recette.qty.astype(float)
        except:
            raise Exception("Please use valid quantities for receipe.")
            
        recettedf = self.units_to_grams(recette, nb_pers)
        
        def get_values(query):
  
            out = self.valeurs_nutritionnelles(query,quiet = True)
            if len(out) == 0:
                #add a line of Nans
                out = out.append(pd.Series(), ignore_index=False)

            return out.iloc[0]
    
        out = recettedf.ingredients.apply(get_values)
        recettedf2 = pd.concat([recettedf,out], axis=1)
        recettedf2['cal_100g'] = recettedf2.energy_100g*self.J_to_cal
        recettedf2['cal'] = recettedf2.qty*recettedf2.energy_100g/100*self.J_to_cal
        recettedf2['weighted_score'] = recettedf2['nutrition-score-fr_100g']*recettedf2.qty/(recettedf2.qty).sum()
        recettedf2['weighted_grade'] = recettedf2.nutriscore_grade*recettedf2.qty/(recettedf2.qty).sum()


        return recettedf2
        
    
    def analyze(self, recette, nb_pers = None):
        
        if (type(recette) is dict) or ('weighted_grade' not in recette.columns):
            
            recette = self.compute_receipe(recette, nb_pers = None)
        
        result = recette.sum()
        
        return result
