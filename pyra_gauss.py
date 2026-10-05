import cv2
import numpy as np

def gaussian_pyramid(img, levels):
    """Réalise une pyramide gaussienne de l'image img 
    sur le nombre de niveaux levels"""
    G = [img]                          # niveau 0 = image d'origine
    for i in range(levels - 1):
        G.append(cv2.pyrDown(G[-1]))   # on réduit le dernier niveau obtenu
    return G

def laplacian_pyramid(img, levels):
    """Réalise une pyramide laplacienne de l'image img 
    sur le nombre de niveaux levels"""
    G = gaussian_pyramid(img.astype(np.float32), levels)   # float32 obligatoire
    L = []
    for i in range(levels - 1):
        taille = (G[i].shape[1], G[i].shape[0])            # (largeur, hauteur)
        agrandi = cv2.pyrUp(G[i + 1], dstsize=taille)
        L.append(G[i] - agrandi)
    L.append(G[-1])                                         # résidu
    return L

img = cv2.imread("Cinque-Terre-Manarola/Manarola_under.jpg").astype(np.float32)

#%% Test 1: Affichage des pyramides gaussienne et laplacienne

"""
G = gaussian_pyramid(img, 4)

for i, g in enumerate(G):
    cv2.namedWindow(f"niveau {i}", cv2.WINDOW_NORMAL)   # fenêtre redimensionnable
    cv2.resizeWindow(f"niveau {i}", 500, 350)           # même taille pour tous
    cv2.imshow(f"niveau {i}", g)
cv2.waitKey(0)


L = laplacian_pyramid(img, 4)

for i, l in enumerate(L):
    print(f"niveau {i} : {l.shape}  min={l.min():.1f}  max={l.max():.1f}")
    if i < len(L) - 1:
        affichage = np.clip(l + 128, 0, 255).astype(np.uint8)   # on recentre sur gris moyen
    else:
        affichage = np.clip(l, 0, 255).astype(np.uint8)
    cv2.namedWindow(f"laplace {i}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"laplace {i}", 500, 350)
    cv2.imshow(f"laplace {i}", affichage)
cv2.waitKey(0)
"""

def collapse(L):
    """Reconstruit l'image à partir de sa pyramide laplacienne L"""
    img = L[-1]                                          # on part du résidu
    for lvl in reversed(L[:-1]):                         # du plus petit au plus grand
        taille = (lvl.shape[1], lvl.shape[0])
        img = cv2.pyrUp(img, dstsize=taille) + lvl       # on réagrandit puis on rajoute les détails
    return img

#%% Test 2: Reconstruction de l'image à partir de sa pyramide laplacienne

"""
L = laplacian_pyramid(img, 4)

rec = collapse(L)

print("erreur max :", np.abs(rec - img).max())
cv2.namedWindow("reconstruction", cv2.WINDOW_NORMAL)
cv2.resizeWindow("reconstruction", 700, 500)
cv2.imshow("reconstruction", np.clip(rec, 0, 255).astype(np.uint8))
cv2.waitKey(0)
"""
#%% Test 3: Fusion d'images par méthode naive

#a partir d'ici fusion d'image d'abord par méthode naive puis on essaie de quantifier le contraste

def pyramid_blend(A, B, mask, levels):
    LA = laplacian_pyramid(A, levels)                       # détails de A, niveau par niveau
    LB = laplacian_pyramid(B, levels)                       # détails de B
    Gm = gaussian_pyramid(mask.astype(np.float32), levels)  # masque de plus en plus flou

    L_R = []
    for la, lb, gm in zip(LA, LB, Gm):
        gm = gm[..., None]                  # (h, w) -> (h, w, 1) pour multiplier les 3 canaux
        L_R.append(gm * lb + (1 - gm) * la) # formule 6, à chaque niveau

    return collapse(L_R)                    # on reconstruit l'image

"""
A = cv2.imread("Cinque-Terre-Manarola/Manarola_under.jpg").astype(np.float32)
B = cv2.imread("Cinque-Terre-Manarola/Manarola_over.jpg").astype(np.float32)
B = cv2.resize(B, (A.shape[1], A.shape[0]))     # même taille obligatoire

# masque : 0 à gauche (on prend A), 1 à droite (on prend B)
mask = np.zeros(A.shape[:2], np.float32)
mask[:, A.shape[1] // 2:] = 1.0

naif = mask[..., None] * B + (1 - mask[..., None]) * A
multi = pyramid_blend(A, B, mask, levels=20)

for nom, im in [("naif", naif), ("pyramide", multi)]:
    cv2.namedWindow(nom, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nom, 800, 550)
    cv2.imshow(nom, np.clip(im, 0, 255).astype(np.uint8))
cv2.waitKey(0)
"""
# Premier critere de choix le contraste

def contrast(img):
    gris = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gris, cv2.CV_32F)      # CV_32F pour garder les valeurs négatives
    return np.abs(lap)

"""
img = cv2.imread("Cinque-Terre-Manarola/Manarola_over.jpg").astype(np.float32)/255.0
C = contrast(img)
print("forme :", C.shape, " min :", C.min(), " max :", C.max())

affichage = np.clip(C / np.percentile(C, 99), 0, 1)
cv2.namedWindow("contraste", cv2.WINDOW_NORMAL)
cv2.resizeWindow("contraste", 800, 550)
cv2.imshow("contraste", affichage)
cv2.waitKey(0)
"""