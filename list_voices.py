"""Lista las voces de Chatterbox (NVIDIA Riva) para saber el nombre exacto
de la voz en español y ponerlo en config.py → RIVA_VOICE.

Requisito:  venv\\Scripts\\pip install nvidia-riva-client
Uso:        venv\\Scripts\\python list_voices.py
"""

import riva.client
from sparky.config import RIVA_SERVER, RIVA_FUNCTION_ID, CLOUD_API_KEY

auth = riva.client.Auth(
    uri=RIVA_SERVER, use_ssl=True,
    metadata_args=[
        ["function-id", RIVA_FUNCTION_ID],
        ["authorization", "Bearer " + CLOUD_API_KEY],
    ],
)
service = riva.client.SpeechSynthesisService(auth)

try:
    from riva.client.proto import riva_tts_pb2
    cfg = service.stub.GetRivaSynthesisConfig(riva_tts_pb2.RivaSynthesisConfigRequest())
    print("\n=== Voces disponibles (busca 'es' para español) ===")
    for m in cfg.model_config:
        p = dict(m.parameters)
        print(f"  {p.get('voice_name','?'):45} | {p.get('language_code','?')}")
except Exception as e:
    print(f"No pude listar por API ({e}).")
    print("Usa el comando oficial:")
    print('  git clone https://github.com/nvidia-riva/python-clients.git')
    print(f'  python python-clients/scripts/tts/talk.py --server {RIVA_SERVER} --use-ssl \\')
    print(f'    --metadata function-id "{RIVA_FUNCTION_ID}" \\')
    print('    --metadata authorization "Bearer TU_CLAVE" --list-voices')
