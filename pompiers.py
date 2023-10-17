import streamlit as st
import pandas as pd
pd.set_option('display.max_columns', 60)
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import  RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, classification_report

#### INTÉGRATION DU FICHIER CSS 
with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

#### TITRE DU STREAMLIT
st.title("Temps de réponse - Brigade des Sapeurs Pompiers de Londres")

#### CRÉATION DE LA SIDEBAR
sidebar_title = '<p style="color:White; font-size: 26px;">Sommaire</p>'
st.sidebar.markdown(sidebar_title, unsafe_allow_html=True)

pages=["Introduction", "Enrichissements & Data Cleaning","DataVizualization", "Modélisation",
       "Conclusion"]
page=st.sidebar.radio('', pages)

st.sidebar.divider()
st.sidebar.markdown('Auteurs')

st.sidebar.markdown('- <p style="font-size: 14px"> Alia Boudehane | <a href="https://www.linkedin.com/in/alia-boudehane-704172185/" style="color: white;font-size: 14px">LinkedIn</a></p>\
                    \n- <p style="font-size: 14px"> Doravann Chou | <a href="https://www.linkedin.com/in/doravann-chou-81a999269" style="color: white;font-size: 14px">LinkedIn</a></p>\
                    \n- <p style="font-size: 14px"> Maïna Le Roux | <a href="https://www.linkedin.com/in/mainaleroux" style="color: white;font-size: 14px">LinkedIn</a> </p>', unsafe_allow_html=True)


#### PAGE 1 : INTRODUCTION

if page == pages[0] : 
  st.image('lfb2.jpeg')
  st.header("Introduction")
  st.subheader('Le Sujet')
  st.markdown("La **:red[London Fire Brigade (LFB)]** est le service d'incendie et de secours le plus actif du pays.\
           Fondée en 1886, elle n'a, depuis lors, cessé de s’améliorer et jouit aujourd’hui d’une réputation reconnue\
            en matière de lutte contre les incendies et de secours d'urgence, faisant d’elle l'une des institutions les\
            plus emblématiques et respectées du pays. \n\n Sur l’année 2014, ils seront notifiés comme étant les sapeurs-pompiers les plus occupés\
            dans le monde en comptabilisant un total de 171 067 appels d’urgence et en traitant 20934 feux ! \
           \nC’est d’ailleurs l’une des plus grandes organisations de lutte contre les incendies et de secours au monde, agissant dans la protection des personnes\
            et biens contre les incendies sur un périmètre de 1587 kilomètres carrés autour du Grand Londres.\
           \n\n Dans cette étude, nous plongerons dans l'analyse des données liées aux performances passées de la London Fire Brigade, en mettant l'accent\
            sur leur **:red[efficacité de temps de réponse].** \n\nNous allons dans un premier temps prendre connaissance de notre jeu de données\
            qui proviennent du site officiel et gouvernemental de la London Fire Brigade. Nous allons étudier puis nettoyer ces données afin de les rendre\
            les plus lisibles et utiles à notre étude.\
           \n\n Nous utiliserons ensuite des techniques d'analyse de données et des modèles de prédiction pour mieux comprendre les tendances historiques\
            et les facteurs qui influencent ces mesures cruciales.")


  st.subheader('Les Données')
  st.markdown('**:red[Source des Jeux de Données]**')
  st.markdown("Nos jeux données sont disponibles sur le site officiel de la ville de Londres - https://data.london.gov.uk, ce qui nous permet d'avoir une entière confiance\
               en leur provenance et leur intégrité. \n\nDurant la phase exploratoire de notre projet, nous avons également été en contact avec des Business\
               Intelligence Analysts de la London Fire Brigade, qui ont répondu rapidement à nos questions, et nous les en remercions.")
  st.markdown('**:red[Description des Données]**')
  st.markdown("Nous avions deux principaux jeux de données disponibles :\
              \n - **Incident Records** : les détails de chaque incident sur lequel la LFB est intervenu depuis le 1er janvier 2009. Des informations sont\
               fournies sur la date et le lieu de l'incident ainsi que sur le type d'incident. \
              \n - **Mobilisation Records** : les détails de chaque véhicule d'incendie envoyé sur les lieux d'un incident depuis janvier 2009.\
              Des informations sont fournies sur l'engin mobilisé, le lieu d'où il a été déployé et les heures d'arrivée sur les lieux de l'incident.")
  
  col1, col2 = st.columns(2)

  with col1:
    st.write("***Incident Records***")
    metadata = pd.read_csv("Metadata.csv")
    st.dataframe(metadata)
  with col2:
    st.write("***Mobilisation Records***")
    metadata_mobi = pd.read_csv("Mobilisations-Metadata.csv")
    st.dataframe(metadata_mobi)

  st.markdown("Nous disposons de 3 colonnes communes aux 2 jeux de données (*IncidentNumber*, *Calyear*, et *HourOfCall*) à partir desquelles\
               nous allons **fusionner nos tables**.")
  
  st.markdown('**:red[DataFrame Consolidé]**')
  st.markdown("Voici un aperçu de notre DataFrame consolidé, avant toute modification :")

  ## Afficher df.head() après fusion
  df_consolidated = pd.read_csv("df_consolidated.csv",index_col = 0)
  df_consolidated.reset_index(inplace = True)
  df_consolidated = df_consolidated.drop(columns = 'index')
  st.dataframe(df_consolidated)

  st.write("La taille de notre dataframe est : `(2220718, 58)`")

  st.markdown("Pour la suite du projet et notamment la partie modélisation, c'est la variable ***:red[AttendanceTimeSeconds]*** que nous choisissons comme\
              notre **variable cible**. Il s'agit du temps de réponse pour un camion mobilisé, comprenant le temps de préparation de la brigade\
               une fois cette dernière informée ainsi que le temps de trajet pour ce rendre sur le lieu de l'incident.")

#### PAGE 2 : ENRICHISSEMENTS ET DATA CLEANING
if page == pages[1] : 
  st.header("Enrichissements & Data Cleaning")
  st.markdown(" ")

  st.subheader('Nos Enrichissements :fire:')
  st.markdown('**:red[La variable Distance]**')
  st.markdown("Nous avons souhaité ajouter à notre dataset la variable ***:red[Distance]***. Cette dernière représente la distance entre la caserne d'où a été mobilisé\
              le camion et le lieu de l'incident, en mètres. Voici comment nous avons procédé : \n\n - **Collecte de données** : pour chaque caserne, nous avons manuellement\
              collecté leurs coordonnées géographiques, soit les latitudes et longitudes.\
              \n - **Conversion de variables** : les données de latitudes et longitudes des lieux d'incidents étant incomplètes (+50% de Nan), nous avons convertis\
               les données *easting_rounded* et *northing_rounded* en latitude et longitude. Nous perdons légèrement en précision sur la localisation exacte mais de façon\
              tout à fait acceptable. \
              \n - **Calcul de la distance** : à partir des coordonnées géographiques des casernes et des lieux d'incidents, nous avons pû calculer une nouvelle variable : la\
               :red[***Distance*** *(en mètre)*] parcourue pour chaque mobilisation.\
              \n - **Vérification** : pour se rassurer sur la pertinence du calcul effectué, nous avons testé plusieurs distances sur Google Maps.")
  
  with st.expander("Calcul de la Distance (code)"):
    code = '''# Fonction pour calculer la distance en mètres entre deux points géographiques (haversine formula)
def haversine(lat1, lon1, lat2, lon2):
    # Rayon de la Terre en mètres
    radius = 6371000

    # Conversion des degrés en radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Différences de latitudes et de longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Formule de la haversine
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    # Distance en mètres
    distance = radius * c
    return distance

# Appliquer la fonction haversine pour calculer la distance et ajouter une colonne "Distance" au DataFrame
df["Distance"] = df.apply(lambda row: haversine(row["Latitude"], row["Longitude"], row["Station_Latitude"], row["Station_Longitude"]), axis=1) '''
    st.code(code,language='python')

  st.markdown(" ")
  st.markdown('**:red[La variable DateOfCall]**')
  st.markdown("Afin de rendre l'analyse plus facile et d'exploiter d'autres axes nous utilisons la variable *'DateOfCall'* pour créer *'MonthOfCall'* et *'DayOfCall'*.")
  st.markdown(" ")

  st.subheader("DataCleaning :male-firefighter:")
  st.markdown("Sans rentrer dans le détail, expliquer les modifications apportées / sélection des variables.\
              \n Afficher un aperçu de df_final\
              et aussi df.info(), autre information intéressante à ce stade")
  
  st.markdown('**:red[Gestion des Doublons]**')
  st.markdown("Nous n'avions aucun doublon dans notre jeu de données.")

  st.markdown('**:red[Gestion des valeurs manquantes]**')
  st.markdown("Concernant les Nans, nous décidons de supprimer toutes les lignes pour lesquels le pourcentage de Nan dans la colonne est inférieur à 2%.\
               Ensuite, pour le reste des valeurs manquantes et afin d’éviter toute fuite de données durant la modélisation nous ne modifierons que les Nans\
              qui ne nécessitent pas une opération de calcul statistique.\
              \n - *DelayCode_Description (75% de Nans)* : il s'agit de la raison pour laquelle la brigade est arrivée en retard sur le lieu de l’incident. Les Nans\
               correspondent aux mobilisations où il n'y a pas eu de retard (onfirmé par le BI Analyst que nous avons contacté). Nous remplaçons donc remplacés par\
                la veleur 'No Delay'.\
               \n - *SpecialServiceType (78% de Nans)* : cette colonne ne contient des informations que si le type de l’intervention est un 'SpecialService'. Nous\
               remplaçon les 78% de Nan par la valeur 'Not a Special Service'.\
              \n\n Suite à la sélection finale des variables que nous conserverons avant d'entâmer la partie modélisation, notre jeu de données ne présente plus aucun Nan.")

  st.markdown('**:red[Variables Conservées dans notre DataFrame Final]**')
  st.markdown("Voici la liste des variables conservées, avant de démarrer nos premières modélisations :\
              \n\n *'IncidentNumber', 'DateOfCall', 'CalYear', 'HourOfCall',\
              'IncidentGroup', 'StopCodeDescription', 'SpecialServiceType', 'PropertyCategory', 'AddressQualifier', 'BoroughName', 'IncidentStationGround',\
              'NumStationsWithPumpsAttending', 'NumPumpsAttending', 'CallCount', 'ResourceMobilisationId', 'TurnoutTimeSeconds', 'TravelTimeSeconds', 'AttendanceTimeSeconds',\
              'DeployedFromStation_Name', 'PumpOrder', 'DelayCode_Description', 'MobilisationTime', 'MonthOfCall', 'DayOfCall', 'Distance'*")
  
  ## Afficher df.head() avant modélisation
  st.markdown('**Aperçu du DataFrame avant la modélisation**')
  df_modelisation = pd.read_csv("df_modelisation.csv",index_col = 0)
  st.dataframe(df_modelisation)

#### PAGE 3 : DATAVIZ

if page == pages[2] : 
  st.header("DataVizualization")
  st.markdown(" ")
  st.subheader("La variable cible : AttendanceTimeSeconds")
  
  ## DataViz : distribution variable cible
  st.markdown('**:red[Distribution de AttendanceTimeSeconds]**')
  st.markdown("Nous constatons visuellement que la distribution de notre variable cible suit une loi normale. La médiane est à 325 secondes,\
               soit **5 minutes et 25 secondes**. Il s'agit donc ici du temps médian pour une équipe de sapeurs-pompiers de se préparer et ce rendre\
              sur les lieux de l'incident. Le maximum est à 1200 secondes, soit 20 min, et il s'agit du seuil maximum utilisé par la LFB elle-même\
              dans ses différents analyses et rapports.")
  st.image('attendancetime_distribution.jpeg')

  ## DataViz Attendance Time selon carte de Londres
  st.markdown(" ")
  st.markdown('**:red[Cartes de Londres]**')
  
  display = st.radio(':gray[Que souhaitez-vous montrer ?]', (':gray[Temps de Réponse par Quartier]', ':gray[Temps de Réponse par Secteur Caserne]'))
  if display == ':gray[Temps de Réponse par Quartier]':
    ## Map par Quartier
    path_to_html = "map2.html" 
    # Read file and keep in variable
    with open(path_to_html,'r') as f: 
        html_data = f.read()
    # Show in streamlit
    st.components.v1.html(html_data,width=800, height=600)
  elif display == ':gray[Temps de Réponse par Secteur Caserne]':
    ## Map par Station Ground
    path_to_html = "map1.html" 
    # Read file and keep in variable
    with open(path_to_html,'r') as f: 
        html_data = f.read()
    # Show in streamlit
    st.components.v1.html(html_data,width=800, height=600)
  
  ## DataViz Attendance Time selon heure de la journée
  st.markdown(" ")
  st.markdown("**:red[Les Temps de Réponse selon l'Heure de la Journée]**")
  st.markdown("Le graphique ci-dessous nous permet de visualiser le **Temps de Préparation** (TurnoutTime), le **Temps de Trajet** (TravelTime)\
              et le **Temps de Réponse** total (AttendanceTime) des brigades selon l'heure de la journée.")
  path_to_plot1 = "plot1.html" 
  with open(path_to_plot1,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=1000, height=450)

  with st.expander(label = "Lecture du graphique"):
    st.write("**Constat temps de trajet :** Assez logiquement, nous observons que le temps de trajet pour se rendre sur le lieu de l'incident\
              est plus important en journée, au moment où le trafic routier est plus dense. Le temps de trajet est plus rapide entre 21h le soir et 9h le matin.\
            \n\n **Constat temps de trajet temps de préparation (Turnout) :**  Il est intéressant de voir qu'il existe une différence du temps de préparation\
             des équipes entre minuit et 7h du matin. Est-ce dû au fait qu'il y a moins de personnel la nuit ?\
             \n\n**Constat temps de réponse total :** Le temps de réponse total est la somme des deux temps précédents. Les temps forts / faibles de chacune\
              des deux variables précédentes font que le temps total s'équilibre sur la journée, à l'exception du créneau 7h - 10h et  20h et Minuit (temps de trajet ET temps de préparation rapides).")

  ## DataViz Temps de trajet selon le retard
  st.markdown(" ")
  st.markdown("**:red[Temps de Trajet moyen selon la raison du retard]**")
  st.markdown("Le graphique ci-dessous nous permet de visualiser le **Temps de Trajet moyen** (en secondes toujours) selon la raison du retard. Lorsqu'il n'y a pas eu de retard,\
              cela est représenté par la valeur '*No delay*'.")
  path_to_plot5 = "plot5.html" 
  with open(path_to_plot5,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=800, height=450)

  with st.expander(label = "Lecture du graphique"):
    st.write("**Constat :** Sans surprise, lorsqu'il n'y a pas de retard le temps de trajet est exemplaire. Par ailleurs, le motif d' *'Adresse incomplète'*\
            est celui qui fait le plus perdre de temps aux equipes, suivi d'une autre cause moins explicite qui indique que l'équipe est arrivée mais\
            qu'elle a été retenue pour une autre raison ou encore que l'équipe était déjà en intervention à l'exterieur au moment de l'appel par le centre de contrôle.")

## DataViz Temps de réponse et Distance
  st.markdown(" ")
  st.markdown("**:red[Temps de Trajet moyen et Distance moyenne parcourue par Quartier]**")
  st.markdown("Le graphique ci-dessous affiche par quartier de Londres le Temps de Réponse moyen ainsi que la Distance moyenne parcourue")
  
  path_to_plot6 = "plot6.html" 
  with open(path_to_plot6,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=1000, height=450)

  with st.expander(label = "Lecture du graphique"):
    st.write("**Constat :** Alors que nous pensions plus évidente la corrélation entre le Temps de Réponse et la Distance, nous constatons ici, en regardant ces deux métriques\
             par Quartier de Londres, qu'il n'existe pas de façon évidente une relation entre ces deux variables.")


  st.markdown(" ")
  st.subheader("Le volume d'Incidents et de Mobilisations")

  ## DataViz Nombre d'incidents par année
  st.markdown("**:red[Volume d'incidents par Année]**")
  st.markdown("Le graphique ci-dessous nous permet de visualiser le **Volume d'incidents** selon l'année, avec une disctinction faite selon le **Type d'incident**.")
  path_to_plot7 = "plot7.html" 
  with open(path_to_plot7,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=900, height=450)

  with st.expander(label = "Lecture du graphique"):
    st.write("**Constat :** Nous constatons une grande proportion de fausse alarme dans laquelle nous avons une majorité AFA- Automatic Fire Alarm (alarme déclenchée automatiquement\
            par les detecteurs de fumée). Concernant les feux il y a majoritairement des feux de grande ampleur.\
             \n\n Au cours des années le volume d'incidents varie sensiblement, cependant nous constatons un accroissement constant depuis 2015.\
             \n\n L'année 2023 n'étant pas finie elle n'est pas encore éligible à une bonne lecture, nos données s'arretent à Juillet 2023 soit 60% de l'année , si la tendance moyenne\
              d'évolution du volume d'incident du mois reste la même nous pourrions nous attendre à avoir un volume dépassant les 170 000 incidents d'ici la fin de l'année.\
             Une estimation qui vient se rapprocher des résultats de l'année 2022.") 

  ## DataViz Nombre d'incident selon heure de la journée
  st.markdown(" ")
  st.markdown("**:red[Nombre d'Incidents selon Heure de la Journée]**")
  st.markdown("Le graphique ci-dessous nous permet de visualiser le **Volume d'incidents** selon l'heure de la journée, avec une disctinction faite selon le **Type d'incident**.\
              Il est également possible d'afficher l'année de son choix.")
  path_to_plot2 = "plot2.html" 
  with open(path_to_plot2,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=900, height=450)

  with st.expander(label = "Lecture du graphique"):
    st.write("**Constat :** Il est nettement visible - et c'est assez logique - qu'il existe une différence du volume d’incidents selon l’heure de la journée\
            et cela quelque soit l'année. Le graphique nous montre également une surreprésentation des incidents de type “False Alarm”.")

  ## DataViz Nombre de mobilisation par quartier
  st.markdown(" ")
  st.markdown("**:red[Répartition des Mobilisations par Quartier]**")
  st.markdown("Le graphique ci-dessous nous permet de visualiser la **quantité de mobilisations** selon les quartiers de Londres, **depuis 2009**,\
              en mettant également en avant le type d'incident. Les quartiers sont triés de façon descendante selon la moyenne du Temps de Réponse ")
  path_to_plot3 = "plot3.html" 
  with open(path_to_plot3,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=1000, height=450)

  with st.expander(label = "Lecture du graphique"):
    st.write("**Constat :** Nous observons que certains des quartiers qui ont un bon temps de réponse ont aussi une grosse proportion de fausses alarmes. Aussi,\
             la quantité d'incidents ne semble pas influencer la performance de rapidité du temps de réponse. Le type d'incident ne doit donc que partiellement\
            influencer la disparité des performances par quartier.")


#### PAGE 4 : MODELISATION

if page == pages[3]:
  st.header("Modelisation")

  #df = pd.read_csv("df_final2.csv", low_memory = False, index_col = 0)

  st.write("En premier lieu nous devons nettoyer notre jeu de données et supprimer les colonnes que nous avions gardé pour la DataVisualisation.\
  \nNous supprimons les colonnes d'identification (ID), la colonne DateOfCall qui répètent les informations de Day0fCall, MonthOfCall et CalYear ainsi que les colonnes TurnoutTimeSeconds et TravelTimeSeconds afin d’éviter une fuite donnée qui donneraient à tort une surperformance à notre modèle de prédiction, car elles permettent de calculer notre variable cible.")

  st.write("Ensuite nous réduisons notre jeu de données en ne gardant que les informations postérieures à 2015 car une dizaine de caserne ont fermé fin 2014 dans le cadre d’un plan de secours de sauvegarde financière. \
  \nCe choix a été fait afin de ne pas fausser les estimations sur ces casernes qui seraient sous représentées et afin également de supprimer les Nans présents dans la colonne Distance pour ces casernes.")

  st.write("Pour continuer ce nettoyage nous avons modifié le type de certaines variable numérique en catégorielle car ce sont des indicateurs temporels et qu’il ne faut pas que le modèle de prédiction cherche à les quantifier ou les ordonner.")


  # REDUCTION DE DIMENSIONS
  st.subheader("Reduction de dimensions")

  st.write("Nous avons donc maintenant un jeu de données de taille `(1295782, 20)`. Nous avons donc décidé de tenter une réduction de dimensions, après avoir encodé nos variables catégorielles et standardiser nos données, nous nous retrouvons avec 351 colonnes et une explication de la variance comme suit : ")
  
  st.image("pca_variance.png")
  with st.expander(label = "Lecture du graphique"):
    st.write("Nous  constatons une chute à environ 40 nombres de facteurs, voyons voir ce que cela représente en terme de pourcentage.")

  st.image("pca_ratio.png")
  with st.expander(label = "Lecture du graphique"):
    st.write("Cela ne représente que 30% de notre jeu de données, c'est peu. Par curiosité, nous visualisons avec deux axes ce que cela représente.")

  st.image("cercle.png")
  with st.expander(label = "Lecture du graphique"):
    st.write("Comme nous nous y attendions, cela n'est pas très parlant, plusieurs groupes de variables semblent être bien corrélées entre elles mais il n'y a aucun intérêt à réduire ici les dimensions sur deux axes puisque les corrélations avec les axes sont très faibles, la plupart d’entre elles ne dépassent même pas les 0.2, -0.2. \n\n Nous ne pouvons donc pas nous aider des réductions de dimensions pour réduire notre jeu de données.")
    
  # CORRELATIONS
  st.subheader("Corrélations")

  st.write("Afin d’optimiser notre modèle de prédictions nous décidons d’étudier les corrélations entre les variables explicatives et la variable cible.")

  st.markdown("- ##### Variables Numériques")

  # Heatmap
  st.image("heatmap.png")
  with st.expander(label = "Lecture du graphique"):
    st.write("A l'aide de cette heatmap, nous décidons de supprimer les colonnes CallCount et MobilisationTime car ce sont celles qui sont le moins corrélées à notre variable cible AttendanceTimeSeconds.")
  

  st.markdown("- ##### Variables Catégorielles")
  # Test Anova
  anova = pd.read_csv("anova.csv")
  st.dataframe(anova)

  with st.expander(label = "Lecture du tableau"):
    st.write("Le résultat est sans appel, toutes nos variables explicatives sont corrélées à notre variable cible. Nous décidons donc de toutes les garder.")



  # MODELISATION
  st.subheader("Modélisation")  

  st.write("Notre objectif est d’obtenir un score de test supérieur à 70%.\
  \nNotre variable cible est une variable continue, ce qui signifie que nous avons à faire à une méthode de régression. Après encodage de notre jeu de données\
   nous avons un data frame de taille `(1295782 , 363)`.\
  \n\n Notre tâche sera d’estimer en fonction des informations fournies, le temps d’intervention potentiel.\
  \n \nNous allons essayer les 3 algorithmes suivants :") 
  st.markdown("- Linear Regression \
  \n- Decision Tree Regressor \
  \n- Random Forest Regressor")

  st.write("Pour l’évaluation de la performance de nos prédictions nous disposons du MSE, RMSE, MAE et score R2.")

  #####  RESULTAT DES 3 MODELES REGRESSION##### 
 
  tab1, tab2, tab3 = st.tabs(["Linear Regression", "Decision Tree Regressor", "Random Forest Regressor"])

  with tab1:
    st.image("linear_reg.png")
   
  with tab2:
    st.image("dtr.png")
   
  with tab3:
    st.image("rf.png")

  st.write("Au vu des résultats du score r2, la métrique la plus lisible, nous avons pu déterminer que le Random Forest est l’algorithme le plus performant.\
  \nCependant, nous avons un grand dataframe et ce modèle est très énergivore (Plus d’une heure d'execution).\
  \nNous décidons donc de convertir nos valeurs dans notre variable cible en différentes classes afin de simplifier notre prédictions en une classification.")

  st.write("Pour déterminer la séparation de ces classes, nous observons la distribution de notre variable cible.")

  path_to_plot6bis = "plot6_bis.html" 
  with open(path_to_plot6bis,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=800, height=400)

  st.write("Nous décidons de séparer notre variables en 5 classes avec , 1 classe par quartile puis 1 classe pour les valeurs extrêmes.")

  path_to_plot7bis = "plot7_bis.html" 
  with open(path_to_plot7bis,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=910, height=450)


  st.write("Etant donné que notre variable cible est dorénavant une variable catégorielle, nous décidons de re-lancer un test de corrélation, nous choisirons le test de khi2 d’indépendance:")

  # Test Khi2 d'indépendance
  khi2 = pd.read_csv("khi2.csv")
  st.dataframe(khi2) 

  with st.expander(label = "Lecture du tableau"):
    st.write("Encore une fois, nous constatons que la variable cible est bien dépendante de toutes les variables explicatives.\
    \nNous conservons donc toutes les variables catégorielles.")

  st.write("Nous allons relancer 3 nouveaux modèles , de classification cette fois ci :") 
  st.markdown("- Logistic Regression \
  \n- Decision Tree Classifier \
  \n- Random Forest Classifier")

  st.write("Cette fois-ci, étant donné qu’il s’agit d’un modèle de classification, nous utiliserons le R2 score, le rapport de classification ainsi qu’un tableau de confusion pour évaluer la performance des différents modèles. L’ensemble de ces métriques nous apporte des informations importantes sur notre résultat.")


  #####  RESULTAT DES 3 MODELES CLASSIFICATION (5 CLASSES) ##### 
  tab1, tab2, tab3 = st.tabs(["Logistic Regression", "Decision Tree Classifier", "Random Forest Classifier"])

  with tab1:
    st.image("lr5.png")
    
  with tab2:
    st.image("dt5.png")

  with tab3:
    st.image("rf5.png")
    

  st.write("Random Forest est encore une fois le modèle le plus performant et cette fois-ci l'exécution est nettement plus rapide(moins de 10min), nous allons approfondir nos recherches sur ce modèle.\
  \n\nTout d'abord nous allons modifier la classification car beaucoup de valeurs écartées se retrouvent dans la même classe,nous allons donc les répartir par temps similaire plutôt que par part égales de valeurs. En effet la classe 5 a un très mauvais recall, cela se comprend par le fait qu’il s’agit de valeurs extrêmes, elles sont moins bien représentées pour commencer mais aussi elles sont moins logiques pour le modèle de prédictions donc plus difficile encore à prédire.\
  \n\nEnsuite nous étudierons les features importantes afin de visualiser si certaines colonnes peuvent être supprimées.\
  \n\nPour finir nous nous pencherons sur les hyperparamètres.")

  # ETAPE 1: LES CLASSES
  st.markdown("- ##### Etape 1: Retravailler les classes")

  st.write("Nous décidons de réduire nos classes, afin de déterminer la séparation de ces classes, nous observons les zones où se regroupent les temps les plus similaires. Pour cela nous ferons deux test:\
  \n\n Le premier test avec 4 classes. \
  \nPour ce qui est de la classe 4 nous décidons d’y inclure les valeurs les plus fortes plus les valeurs extrêmes ce qui semble être le plus logique pour la compréhension de ces valeurs extrêmes.\
  \nNous avons donc :\
  \nClasse 1(Temps rapide) : De 0 à 2:48 (2 min et 48 sec)\
  \nClasse 2(Temps moyen): De 2:48 à 5:48\
  \nClasse 3(Temps long): De 5:48 à 10:24\
  \nClasse 4(Temps très long) : De 10:24 à 20min.")

  path_to_plot8 = "plot8.html" 
  with open(path_to_plot8,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=910, height=450)

  st.write("Le deuxième test avec 3 classes. \
  \nNous avons donc :\
  \nClasse 1(Temps rapide) : De 0 à 4:04 (2 min et 48 sec)\
  \nClasse 2(Temps moyen): De 04:04 à 10:24\
  \nClasse 3(Temps long): De 10:24 à 20min")

  path_to_plot9 = "plot9.html" 
  with open(path_to_plot9,'r') as f:
    html_data = f.read()
  st.components.v1.html(html_data,width=910, height=450)

  st.write(" Observons les résultats")

  

  ##### RESULTAT DES 2 MODELES (4 classes et 3 classes) ##### 

  option = st.selectbox(
    'Choissisez le nombre de classes pour voir le résultat',
    ('4 classes', '3 classes'))
  
  if option == "4 classes":
    st.image("rf_4.png")

  if option == "3 classes":
    st.image("rf_3.png")


  with st.expander(label = "Lecture des résultats"):
    st.write("Les classes sont toutes bien prédites et nous avons un très bon score ainsi que de bons résultats de precision, recall et donc de F1\
    \nNous allons maintenant tenter d'affiner la performance grâce aux features performances.")

  # ETAPE 2 : FEATURES IMPORTANCES
  st.markdown("- ##### Etape 2 : Features Importances")

  st.image("features.png")

  with st.expander(label = "Lecture des résultats"):
   st.write("Etant donné que nos variables catégorielles ont été encodé, nous avons un affichage de ces variables par valeurs.\
    \n\nNous automatisons un calcul qui nous donnera la feature importance par variable complète.\
  Nous constatons que les variables PropertyCategory, StopCodeDescription, SpecialServiceType et IncidentGroup sont les moins impactantes sur le jeu de données.") 
   
  st.image("full_features.png")

  st.write("Nous décidons donc de les supprimer une par une pour voir si cela améliore la performance de notre modèle de prédiction.\
  \nMalgré le fait qu'elles aient une faible importance à chaque que nous retirons une variable, nous nous rendons compte que le modèle est (légèrement) moins performant.\
  \nNous décidons de les garder\
  \nNotre dernière étape pour l'amélioration de notre performance est de déterminer les meilleurs hyperparamètres pour notre modèle de prédictions.")

  # ETAPE 3 : HYPERPARAMETRES
  st.markdown("- ##### Etape 3 : Hyperparamètres")

  st.write("Afin de connaître rapidement quelles seraient les meilleures hyperparamètres, nous allons utiliser la validation croisée (cross-validation) pour évaluer différentes combinaisons d'hyper paramètres et choisir celle qui donne les meilleures performances.\
  \nPour cela, nous nous servirons de SearchGridCV dont voici les résultats: ")

  st.image("SearchGridCV.png")
  st.write("Résultat:")
  st.image("Search_results.png")

  st.write("Nous garderons donc la configuration suivante")
  st.image("best_hyperparametre.png")

  st.write("Voici le résultat final")

  ##### DERNIER RESULTAT  #####

  st.image("rf3h.png")


  st.success("Nous avons atteint notre objectif !\
  \n\n Nous avons légèrement amélioré notre prédiction, le résultat est atteint et nous en sommes très satisfait.",icon ="🎉")


























#### PAGE 5 : CONCLUSION  

if page == pages[4]:
  st.markdown(" ")
  st.image('lfb1.svg.png', width = 300)
  st.header('Conclusion')

  st.markdown("Afin de traiter au mieux notre sujet, le choix de notre variable cible s’est donc porté sur :red[**AttendanceTimeSeconds**].\
              Il s'agit du temps (en secondes) entre le moment où la brigade reçoit l'alerte et le moment où elle arrive sur le site de l’incident.")
  # Partie 1

  st.subheader("DataViz et Modélisation")

  st.markdown("Les indicateurs de position, de dispersion, loi normale, les corrélations, \
              nous ont permis de prendre des décisions sur les choix que nous avons faits pour constituer le modèle nous permettant \
              de prédire au mieux le temps de réponse en fonction des différents facteurs pouvant influencer notre valeur cible. \
                  Nous avons pu notamment constater que  les incidents étaient souvent liés à de fausses alertes. \
                      L’heure, la journée, la caserne, le secteur du site d’incident, \
                          pouvaient avoir un impact sur notre variable cible.")

  st.markdown("Ainsi, pour la modélisation, dans un premier temps, \
              nous garderons les colonnes ayant une relation avec catégories citées ci-dessus ou ayant un \
                  faible nombre de valeurs uniques. Pour même accélérer, les calculs, \
                      nous partirons d’un intervalle de données entre 2015 – 2023, faire une réduction des données. \
                          Suite aux tests de régressions, nous nous apercevons des scores très performants, \
                              comme l’on peut le voir ci-dessous :")

         
  left_co, cent_co,last_co = st.columns(3)
  
  with cent_co:
      st.image("perfect_prediction.png", width=200)


  st.markdown("Nous décidons de supprimer les colonnes d’identification et \
              surtout les variables explicatives ayant servies à calculer notre « variable cible ». \
                  Aussi, après concertation avec notre mentor, nous partons sur une logique de classification, \
                      et ensuite travailler sur les classes et les hyper paramètres.")
       
  st.markdown("Le passage à différentes classes, ont permis d'améliorer \
              les modèles avec un  « Random Forest » qui présente un résultat plus performant \
                  que les autres modèles. Les hyper paramètres ont permis d’atteindre notre objectif.")

  st.markdown("Si nous avions voulu aller plus loin, nous aurions pu \
              aller chercher comme nous l'avions fait pour le calcul de la distance, \
                  des informations pouvant influer sur notre valeur cible, tel que la météo, le trafic, la pandémie...")

  st.markdown("Dans le prolongement de notre projet, nous aurions pu aussi utiliser la variable cible \
              'MobilisationTime' pour la modélisation. Et pour une meilleure performance tester \
                  d'autres modèles comme les réseaux de neurones, SVM…")
                  
  # Partie 2
  st.subheader("Bilan des difficultés rencontrées")

  st.markdown("Nous souhaitions également faire le bilan des difficultés rencontrées \
              durant notre projet.  Nous avons en effet rencontré plusieurs problèmes que ce soit durant l’exploitation des \
                  données ou durant les tests de modélisations.")

  st.markdown("Pour ce qu'il est de la partie exploitation des données, voici les quelques principales difficultés rencontrées :")

  st.markdown("<p style='font-size:16px;  text-align: justify;'>\
             <ul><li><strong>Compréhension du jeu de données</strong> de certaines variables : PumpOrder, PlusCode_Description... \
                  Malgré les fichier de metadata présentant une courte description des variables, \
                      certaines interprétations nous semblaient difficiles. Pour s’assurer de la bonne interprétation des données, \
                          nous avons consulté directement des BI Analyst  du site de LFB.</li></ul></p>"
              , unsafe_allow_html=True)

  

  st.markdown("""
              - **Gestion des variables au format Datetime** : Nous avions initialement décidé de travailler  les dates et heures disponibles dans notre jeu de données pour constituer\
               une nouvelle variable cible « Response Time » (valeur cible initiale). Des erreurs détectées dans le format des dates nous a amené à changer la valeur cible ‘AttendanceTimeSeconds’ pour plus de facilité et après discutions avec notre mentor.
              """)
                
  st.markdown("""- **Une volumétrie importante :**\
              \n  * **58 colonnes** qui nous ont rendu le choix difficile dans la sélection/suppression des ces dernières.\
              \n  *  **2,2 millions de lignes** qui ont ralenti l'exécution de certaines tâches (calculs, dataviz, modèles prédictifs), et qui ont également\
              rendu difficile la lecture des graphes de distribution. En effet, bien que nos variables numériques suivent majoritairement une distribution de type\
              loi normmale, la grande présence d'outliers est une des difficultés que nous avons rencontrée.""")
        
  st.markdown("Le choix a été de supprimer les données avant 2015, un choix fait en raison de la fermeture des casernes.\
              Le site officiel  précise aussi que depuis Janvier 2014, 10 stations avaient fermé leur porte.\
              Nous prendrons ainsi les données à partir de 2015 afin d’alléger notre dataset.")
  
  # Partie 3  
  st.subheader("Notre retour d’expérience")   
            
  st.markdown("Il nous semblait également important de partager notre retour d’expérience global sur ce projet, réalisé dans le cadre de notre formation Data Analyst chez DataScientest.")

  st.markdown("D’une part, nous avons eu une très bonne dynamique de groupe, avec une répartition des tâches équitable, dans un environnement d'entraide et de joie de partager ses connaissances.\
              \n\n D’autre part, nous tenions à remercier l’équipe de DataScientest, organisme grâce auquel nous avons suivi notre formation de DataAnalyst,\
              de nous avoir permis d'apprendre dans les meilleures conditions.")
  
  st.markdown("Merci également à notre mentor Mr Yazid Msaadi pour son accompagnement et sa précieuse aide. Il a su nous guider dans l’atteinte de notre objectif sur ce projet fil rouge.")
  
  st.markdown("Merci à l’équipe d’animation des Masterclass, avec qui nous avons envie d’en apprendre encore plus et qui nous a permis d’avoir en temps et en heure les connaissances pour l’avancement de notre projet. Enfin un merci à l’équipe de support, proactive sur nos demandes.")
  
