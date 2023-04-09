from constants import * 
# ----------------------------------------------------------------------------
#                  DO NOT MODIFY THIS PIECE OF CODE    
#
#-----------------------------------------------------------------------------



# Dictionnaire des parametres du fichier pong.cfg
#
# le nom du parametre a affecter

# pour les listes
# p0 : le nom de la fonction à appeler
# p1 : le nom de la valeur par defaut a renvoyer 


D_PARAMS        = {
                    'BORDERLESS' : BORDERLESS,
                    'LEVEL'      : ['__get_level',DEFAULT_LEVEL.name],
                    'P1_UP'      : ['__update_keycode',DEFAULT_P1_UP],    # on definit a la place de None la fonction de retour Key
                    'P1_DOWN'    : ['__update_keycode',DEFAULT_P1_DOWN],
                    'P2_UP'      : ['__update_keycode',DEFAULT_P2_UP],
                    'P2_DOWN'    : ['__update_keycode',DEFAULT_P2_DOWN]

                  }




ALLOWED_KEYS={
                'K_0':py.K_0,
                'K_1':py.K_1,
                'K_2':py.K_2,
                'K_3':py.K_3,
                'K_4':py.K_4,
                'K_5':py.K_5,
                'K_6':py.K_6,
                'K_7':py.K_7,
                'K_8':py.K_8,
                'K_9':py.K_9,
                'K_a':py.K_a,
                'K_b':py.K_b,
                'K_c':py.K_c,
                'K_d':py.K_d,
                'K_e':py.K_e,
                'K_f':py.K_f,
                'K_g':py.K_g,
                'K_h':py.K_h,
                'K_i':py.K_i,
                'K_j':py.K_j,
                'K_k':py.K_k,
                'K_l':py.K_l,
                'K_m':py.K_m,
                'K_n':py.K_n,
                'K_o':py.K_o,
                'K_p':py.K_p,
                'K_q':py.K_q,
                'K_r':py.K_r,
                'K_s':py.K_s,
                'K_t':py.K_t,
                'K_u':py.K_u,
                'K_v':py.K_v,
                'K_w':py.K_w,
                'K_x':py.K_x,
                'K_y':py.K_y,
                'K_z':py.K_z,
                'K_UP':py.K_UP,
                'K_DOWN':py.K_DOWN,
                'K_LEFT':py.K_LEFT,
                'K_RIGHT':py.K_RIGHT,
                'K_LSHIFT':py.K_LSHIFT,
                'K_LCTRL':py.K_LCTRL,
                'K_LALT':py.K_LALT,
                'K_RSHIFT':py.K_RSHIFT,
                'K_RCTRL':py.K_RCTRL,
                'K_RALT':py.K_RALT,
                'K_PAD0':py.K_KP_0,
                'K_PAD1':py.K_KP_1,
                'K_PAD2':py.K_KP_2,
                'K_PAD3':py.K_KP_3,
                'K_PAD4':py.K_KP_4,
                'K_PAD5':py.K_KP_5,
                'K_PAD6':py.K_KP_6,
                'K_PAD7':py.K_KP_7,
                'K_PAD8':py.K_KP_8,
                'K_PAD9':py.K_KP_9,
                'K_KPPLUS':py.K_KP_PLUS,
                'K_KPMINUS':py.K_KP_MINUS,
                'K_KPENTER':py.K_KP_ENTER
             }             
# param1 : string
# param2 : la chaine name par defaut ici : 'normal'
def __get_level(levelselected,defaultlevel):
    
    global BAT_H
    global SPD_BALL
    global SPD_BAT
        
    try:
        level = levelselected.lower()
        # modification des valeurs nécessaires 
        SPD_BALL    *= Level[level].value[0]
        SPD_BALL    = int(SPD_BALL)
        BAT_H       *= Level[level].value[1]
        BAT_H       = int(BAT_H)
        SPD_BAT     *= Level[level].value[2]
        SPD_BAT     = int(SPD_BAT)
        
    except Exception as e: 
        # le name n'existe pas
        print(f"ERR: {e} -> utilisation du niveau par défaut : {defaultlevel}") 

     

# modify keyboard codes
def __update_keycode(key,defaultkey):
    
    # debug 
    # fin debug
    found = False
    for v in ALLOWED_KEYS:
        if v == key:
            found=True
            break
    if found:
        return ALLOWED_KEYS[key]
    else: # retour valeur par defaut
        return ALLOWED_KEYS[defaultkey]
        

nberr = 0
line = ""
try:
    with open(CFG_FILE,'r') as f:
        for line in f:
            if line.strip()=='':
                continue
            cont = False
            for rem in REMARKS:
                if line.strip()[len(rem)-1] == rem:
                    cont = True
                    break
            if cont:   # remarque trouvé
                continue
            
            ch=line.split(SEP,maxsplit=1)
            if not len(ch)==2:
                continue
           
            # Lecture clés dans le dictionnaire
            for key in D_PARAMS:
                if ch[0].upper().strip() == key.upper().strip():
                    try:
                        if type(D_PARAMS[key])==list:
                            param = ch[0].upper().strip() + "=" + D_PARAMS[key][0] + "('" + ch[1].strip() + "','" + D_PARAMS[key][1] +"')"
                            #print(f"BAT_H:{BAT_H}  SPD_BALL:{SPD_BALL}")
                            exec(param)
                        else:
                            param = ch[0].upper().strip() + "=" + ch[1].strip()
                            exec(param)

                    except Exception as e:
                        print(f"ERR: dans le fichier {CFG_FILE} : {str(e)}")
                        # en cas d'erreur on prend la valeur par defaut
                        param = key + "=" + D_PARAMS[key]
                        exec(param)
                        nberr += 1

                    
            

except FileNotFoundError as e :
    print(f"WARN: {str(e)}, utilisation des paramètres par défaut")
    nberr += 1

if nberr > 0:
	print(f"{nberr} erreur(s) dans le fichier {CFG_FILE}")