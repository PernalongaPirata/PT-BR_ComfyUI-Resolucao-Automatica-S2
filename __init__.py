class ResolucaoAutomatica:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "custom_base_size": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 4096, 
                    "step": 8,
                    "tooltip": "Deixe 0 para usar os padrões de 1024 (FLUX/SDXL). Digite 512 para SD1.5, etc."
                }),
                "upscale_factor": ("FLOAT", {
                    "default": 1.5,
                    "min": 1.0,
                    "max": 4.0,
                    "step": 0.05,
                    "tooltip": "Fator de upscale. O padrão 1.5 aumenta a resolução em 50% mantendo múltiplos de 8."
                }),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "upscale_width", "upscale_height", "batch_size")
    FUNCTION = "calculate"
    CATEGORY = "Custom/Logic"

    def calculate(self, image, custom_base_size, upscale_factor):
        batch_size, h, w, _ = image.shape
        ratio = w / h
        base = 1024 if custom_base_size == 0 else custom_base_size

        short_side = int((base * 0.8125) // 8 * 8)
        long_side = int((base * 1.1875) // 8 * 8)

        # 1. Descobre se é paisagem, retrato ou quadrado e define a base
        if ratio > 1.15: 
            base_w, base_h = long_side, short_side
        elif ratio < 0.85: 
            base_w, base_h = short_side, long_side
        else: 
            base_w, base_h = base, base

        # 2. Calcula o upscale em cima da base descoberta, forçando o múltiplo de 8
        up_w = int((base_w * upscale_factor) // 8 * 8)
        up_h = int((base_h * upscale_factor) // 8 * 8)

        # 3. Entrega os resultados para fora do node
        return (base_w, base_h, up_w, up_h, batch_size)


class ResolucaoVideoAutomatica:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "custom_base_size": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 4096, 
                    "step": 8,
                    "tooltip": "Deixe 0 para resoluções nativas do Wan 480p (640x640, 832x480, 480x832)."
                }),
                "upscale_factor": ("FLOAT", {
                    "default": 1.5,
                    "min": 1.0,
                    "max": 4.0,
                    "step": 0.05,
                    "tooltip": "Fator de upscale para o vídeo. O padrão 1.5 calcula em cima da resolução reconhecida."
                }),
            }
        }

    # Agora o node de vídeo também devolve as 5 informações idênticas ao de imagem para manter o padrão no seu fluxo
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "upscale_width", "upscale_height", "batch_size")
    FUNCTION = "calculate"
    CATEGORY = "Custom/Logic"

    def calculate(self, image, custom_base_size, upscale_factor):
        batch_size, h, w, _ = image.shape
        ratio = w / h

        # 1. Descobre a resolução base padrão reconhecida pelo modelo
        if custom_base_size == 0:
            # Resoluções nativas do Wan 480p travadas quando o valor for 0
            if ratio > 1.15: 
                base_w, base_h = 832, 480
            elif ratio < 0.85: 
                base_w, base_h = 480, 832
            else: 
                base_w, base_h = 640, 640
        else:
            # Se você preencher com outro número de base, ele usa a matemática dinâmica
            short_side = int((custom_base_size * 0.8125) // 8 * 8)
            long_side = int((custom_base_size * 1.1875) // 8 * 8)
            
            if ratio > 1.15: 
                base_w, base_h = long_side, short_side
            elif ratio < 0.85: 
                base_w, base_h = short_side, long_side
            else: 
                base_w, base_h = custom_base_size, custom_base_size

        # 2. Calcula o upscale em cima da resolução resolvida, forçando múltiplos de 8 para evitar quebras no VAE
        up_w = int((base_w * upscale_factor) // 8 * 8)
        up_h = int((base_h * upscale_factor) // 8 * 8)

        # 3. Entrega os resultados prontos para as conexões do ComfyUI
        return (base_w, base_h, up_w, up_h, batch_size)


# Mapeamento para o ComfyUI reconhecer os dois nodes
NODE_CLASS_MAPPINGS = {
    "ResolucaoAutomatica": ResolucaoAutomatica,
    "ResolucaoVideoAutomatica": ResolucaoVideoAutomatica
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolucaoAutomatica": "Resolução Automática (Imagem)",
    "ResolucaoVideoAutomatica": "Resolução Automática (Vídeo)"
}
