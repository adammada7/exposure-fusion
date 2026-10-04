import cv2
import numpy as np

def gaussian_pyramid(img, levels):
    G = [img]                          # niveau 0 = image d'origine
    for i in range(levels - 1):
        G.append(cv2.pyrDown(G[-1]))   # on réduit le dernier niveau obtenu
    return G

def laplacian_pyramid(img, levels):
    G = gaussian_pyramid(img.astype(np.float32), levels)   # float32 obligatoire
    L = []
    for i in range(levels - 1):
        taille = (G[i].shape[1], G[i].shape[0])            # (largeur, hauteur)
        agrandi = cv2.pyrUp(G[i + 1], dstsize=taille)
        L.append(G[i] - agrandi)
    L.append(G[-1])                                         # résidu
    return L

img = cv2.imread("Cinque-Terre-Manarola/Manarola_under.jpg").astype(np.float32)
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
    img = L[-1]                                          # on part du résidu
    for lvl in reversed(L[:-1]):                         # du plus petit au plus grand
        taille = (lvl.shape[1], lvl.shape[0])
        img = cv2.pyrUp(img, dstsize=taille) + lvl       # on réagrandit puis on rajoute les détails
    return img

L = laplacian_pyramid(img, 4)

rec = collapse(L)

print("erreur max :", np.abs(rec - img).max())
cv2.namedWindow("reconstruction", cv2.WINDOW_NORMAL)
cv2.resizeWindow("reconstruction", 700, 500)
cv2.imshow("reconstruction", np.clip(rec, 0, 255).astype(np.uint8))
cv2.waitKey(0)