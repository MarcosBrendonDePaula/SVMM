import os
import json , re

class CustomJSONDecoder(json.JSONDecoder):
    """
    Uma classe personalizada que estende json.JSONDecoder para fornecer decodificação JSON com modificações específicas.
    """
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        """
        Decodifica uma string JSON com a remoção de vírgulas inválidas.
        
        Args:
            s (str): A string JSON para decodificar.
        
        Returns:
            dict: O objeto Python correspondente aos dados JSON decodificados.
        """
        s = self._remove_comments(s)
        s = self._remove_invalid_commas(s)
        return super().decode(s, _w)
    
    def _remove_comments(self, s):
        """
        Remove comentários do formato /* ... */ de uma string JSON.
        
        Args:
            s (str): A string JSON contendo comentários.
        
        Returns:
            str: A string JSON com comentários removidos.
        """
        return re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)
    
    def _remove_invalid_commas(self, s):
        # Remove espaços desnecessários após vírgulas
        s = re.sub(r',\s+', ',', s)
        # Coloca as vírgulas após chaves e colchetes na próxima linha
        s = re.sub(r',(?=\s*[\}\]])', ',\n', s)
        # Remove vírgulas extras dentro de objetos
        s = re.sub(r',(\s*\})', r'\1', s)
        # Remove vírgulas extras após o último elemento
        s = re.sub(r',(\s*[\}\]])', r'\1', s)
        return s

class JasonAutoFix:
    @staticmethod
    def load(filepath, **kwargs):
        if 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8-sig'
        if 'load' not in kwargs:
            kwargs['load'] = {}
        try:
            with open(filepath, 'r', encoding=kwargs['encoding']) as manifest_file:
                return json.load(manifest_file, cls=CustomJSONDecoder, **kwargs['load'])
        except Exception as e:
            raise Exception(f"Erro ao carregar o arquivo JSON: {e}")
    
    @staticmethod
    def save(data, filepath, **kwargs):
        try:
            with open(filepath, 'w') as json_file:
                json.dump(data, json_file, indent=4, **kwargs)
        except Exception as e:
            raise Exception(f"Erro ao salvar o arquivo JSON: {e}")