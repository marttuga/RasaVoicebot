# Rasa_Voicebot
O objetivo principal consiste em desenvolver um sistema IVR (Interactive Voice Response) para disponibilizar uma solução de comunicação inteligente com os clientes da DevScope.
No caso, apresento a Tugs!


# Objetivos Epecíficos
* Fazer um estudo das tecnologias de desenvolvimento de voicebots
* Avaliar as funcionalidades oferecidas por essas tecnologias para determinar a melhor escolha para o projeto
* Desenhar, desenvolver e personalizar o assistente para atender às necessidades da DevScope
* Testar e avaliar o assistente para garantir a sua eficiência

# Implementação
* Configurar do Ambiente Rasa - Anaconda Navigator - Ambiente virtual
* Criar e configurar o projeto Rasa - config.yml, credentials.yml, endpoints.yml
* Implementar os restantes componentes - domain.yml, rules.yml,....
* Colocar o assistente em funcionamento - rasa train, rasa run actions, rasa run -m models --endpoints endpoints.yml --port5002 --credentials credentials.yml, python voice_recognition.py / options: rasa interactive, rasa shell
