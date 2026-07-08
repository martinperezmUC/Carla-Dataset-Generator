import os
import subprocess
import re
from pathlib import Path

class CarlaDetector:
    def __init__(self):
        self.common_paths = [
            Path.home() / "CARLA",
            Path.home() / "carla",
            Path.home() / "Downloads" / "CARLA",
            Path("/opt/carla")
        ]

    def find_carla_root(self) -> str:
        """
        Busca la ruta raiz de CARLA dentro del sistema.

        Returns:
            str: ruta de instalacion de CARLA, si se puede obtener de una de entorno o,
                en su defecto, de una seleccion de rutas comunes.
                Si no es posible, se retorna NONE.
        """
        # Se recomienda utilizar una variable de entorno con el directorio
        carla_root = os.environ.get("CARLA_ROOT")

        if carla_root and Path(carla_root).exists(): # Si existe variable de entorno
            return carla_root
        
        for path in self.common_paths:
            if path.exists() and (path / "CarlaUE4.sh").exists():
                return str(path) # Si se ha instalado en una ruta comun
        
        # Si no se ha encontrado en las rutas usuales
        return None

    def is_carla_running(self) -> bool:
        """
        Comprueba si el simulador se encuentra en ejecucion.

        Returns:
            bool: True si se encuentra en ejecucion.
                False en caso contrario.
        """
        try:
            subprocess.run(
                ["pgrep", "-f", "CarlaUE4"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
        
    def get_available_maps(self, carla_root: str) -> list:
        """
        Lee la carpeta que contiene los mapas del simulador y devuelve una lista con aquellos
        que estan instalados.

        Args:
            carla_root (str): Ruta raiz de CARLA.

        Returns:
            list: Lista con los nombres de los mapas disponibles en el simulador.
                Lista vacia si existiera algun error de rutas.
        """
        if not carla_root:
            return []
        
        maps_path = Path(carla_root) / "CarlaUE4" / "Content" / "Carla" / "Maps"
        if not maps_path.exists(): # Si los mapas no se encuentran en la ruta estandar
            return []
        
        maps = []
        for file in maps_path.rglob("*.umap"):
            name = file.stem
            # Solo se contemplan mapas completos del tipo Town_XY
            if name.startswith("Town") and len(name) == 6 and name[4:].isdigit():
                maps.append(name)
        
        return sorted(list(set(maps)))
    
    def get_carla_version(self, carla_root: str) -> str:
        """
        Intenta obtener la version exacta instalada de CARLA a traves de la carpeta de la API
        de Python.
        Por ejemplo: "0.9.16" o "Unknown".

        Args:
            carla_root (str): Ruta raiz de CARLA.

        Returns:
            str: Version del simulador.
                "Unknown" si no ha sido posible su deteccion.
        """
        if not carla_root:
            return "Unknown"
        
        dist_path = Path(carla_root) / "PythonAPI" / "carla" / "dist"
        if not dist_path.exists():
            return "Unknown"
        
        for file in dist_path.glob("carla-*.whl"):
            match = re.search(r"carla-(\d+\.\d+\.\d+)", file.name)
            if match:
                return match.group(1)
        
        return "Unknown"

    def verify_permissions(self, carla_root: str) -> bool:
        """
        Verifica si el script que permite la ejecucion de CARLA tiene los permisos necesarios
        en Linux, previniendo errores inesperados en la GUI.

        Args:
            carla_root (str): Ruta raiz de CARLA.

        Returns:
            bool: True si los permisos son correctos.
                False si CARLA no dispone de permisos de ejecucion.
        """
        if not carla_root:
            return False
        
        executable = Path(carla_root) / "CarlaUE4.sh"
        
        return executable.exists and os.access(executable, os.X_OK)