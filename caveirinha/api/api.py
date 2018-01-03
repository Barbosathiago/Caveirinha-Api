from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import uuid
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/itsadeadh2/Develop/flask/api/cav.db'

db = SQLAlchemy(app)

# Model de proprietário
class Proprietario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(120))
    contato = db.Column(db.String(25))

# Model de Dp's
class Dp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(120))

# Model de veiculo
class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    placa = db.Column(db.String(8))
    tipo = db.Column(db.String(50))
    ano = db.Column(db.String(12))
    chassis = db.Column(db.String(120))
    numeroMotor = db.Column(db.String(15))
    cor = db.Column(db.String(50))
    proprietario_id = db.Column(db.Integer, db.ForeignKey('proprietario.id'), nullable=False)
    proprietario = db.relationship('Proprietario', uselist=False, backref=db.backref('veiculo', lazy=True))

# Model de Ocorrencias
class Ocorrencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    numeroOcorrencia = db.Column(db.String(50), unique=True)
    localOcorrencia = db.Column(db.String(450))
    dp_id = db.Column(db.Integer, db.ForeignKey('dp.id'), nullable=False)
    dp = db.relationship('Dp', uselist=False, backref=db.backref('ocorrencias', lazy=True))
    tipoOcorrencia = db.Column(db.String(50))
    observacoes = db.Column(db.String(450))
    situacao = db.Column(db.String(50))
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    veiculo = db.relationship('Veiculo',uselist=False, backref=db.backref('ocorrencias', lazy=True))
    data = db.Column(db.Date())

# Retorna todos os veículos
@app.route('/veiculos', methods=['GET'])
def get_all_veiculos():
    veiculos = Veiculo.query.all()

    output = []

    for v in veiculos:
        obj = {}
        obj = veiculo_to_json(v)
        output.append(obj)
    return jsonify({'veiculos': output})

# Retorna um veículo em especifico
@app.route('/veiculos/<public_id>', methods=['GET'])
def get_one_veiculo(public_id: str):
    v = Veiculo.query.filter_by(public_id=public_id).first()

    if not v:
        return jsonify({'message': 'Veiculo nao encontrado.'})

    obj = {}
    obj = veiculo_to_json(v)
    return jsonify({'veiculo': obj})

# Cria um veículo
@app.route('/veiculos', methods=['POST'])
def create_veiculo():
    data = request.get_json()
    print(data['proprietario']['public_id'])
    proprietario = Proprietario.query.filter_by(public_id=data['proprietario']['public_id']).first()
    if not proprietario:
        return jsonify({'message': 'Proprietário nao especificado!'})

    data['proprietario_id'] = proprietario.id
    new_veiculo = Veiculo()
    new_veiculo = json_to_veiculo(data,str(uuid.uuid4()))
    db.session.add(new_veiculo)
    db.session.flush()
    db.session.commit()

    return jsonify({'message': 'Veiculo registrado!', 'public_id': new_veiculo.public_id})

# Atualiza um veículo
@app.route('/veiculos/<public_id>', methods=['PUT'])
def update_veiculo(public_id: str):
    data = request.get_json()
    v = Veiculo.query.filter_by(public_id=public_id).first()

    if not v:
        return jsonify({'message': 'Veiculo nao encontrado.'})

    v.placa = data['placa']
    v.chassis = data['chassis']
    v.numeroMotor = data['numeroMotor']
    v.cor = data['cor']
    v.tipoVeiculo = data['tipoVeiculo']
    v.descricao = data['descricao']
    v.nomeProprietario = data['nomeProprietario']
    v.telefoneProprietario = data['telefoneProprietario']

    db.session.commit()
    return jsonify({'message': 'Veiculo atualizado'})

# Apaga um veículo
@app.route('/veiculos/<public_id>', methods=['DELETE'])
def delete_veiculo(public_id: str):
    data = request.get_json()
    v = Veiculo.query.filter_by(public_id=public_id).first()

    if not v:
        return jsonify({'message': 'Veiculo nao encontrado.'})
    db.session.delete(v)
    db.session.commit()
    return jsonify({'message': 'Veiculo deletado'})

@app.route('/proprietarios', methods=['GET'])
def get_all_proprietarios():
    proprietarios = Proprietario.query.all()
    print(proprietarios)

    output = []

    for prop in proprietarios:
        obj = {}
        obj = proprietario_to_json(prop)
        output.append(obj)
    return jsonify({'proprietaraios': output})

@app.route('/proprietarios/<public_id>', methods=['GET'])
def get_one_proprietarios(public_id: str):
    prop = Proprietario.query.filter_by(public_id=public_id).first()

    if not prop:
        return jsonify({'message': 'Proprietario nao encontrado.'})

    obj = {}
    obj = proprietario_to_json(prop)
    return jsonify({'proprietario': obj})

@app.route('/proprietarios', methods=['POST'])
def create_proprietario():
    data = request.get_json()
    new_prop = Proprietario()
    new_prop = json_to_proprietario(data, str(uuid.uuid4()))
    db.session.add(new_prop)
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Proprietario registrado!', 'public_id': new_prop.public_id})

@app.route('/proprietarios/<public_id>', methods=['PUT'])
def update_proprietario(public_id: str):
    data = request.get_json()
    prop = Proprietario.query.filter_by(public_id=public_id).first()

    if not prop:
        return jsonify({'message': 'Proprietario nao encontrado.'})

    prop.nome= data['nome']
    prop.contato = data['contato']

    db.session.commit()
    return jsonify({'message': 'Proprietario atualizado!'})

@app.route('/proprietarios/<public_id>', methods=['DELETE'])
def delete_proprietario(public_id):
    data = request.get_json()
    prop = Proprietario.query.filter_by(public_id=public_id).first()

    if not prop:
        return jsonify({'message': 'Proprietario nao encontrado.'})
    db.session.delete(prop)
    db.session.commit()
    return jsonify({'message': 'Proprietario deletado'})

# Retorna todas as DPs
@app.route('/dps', methods=['GET'])
def get_all_dps():
    dps = Dp.query.all()

    output = []

    for d in dps:
        obj = {}
        obj = dp_to_json(d)
        output.append(obj)
    return jsonify({'dps': output})

# Retorna uma DP específica
@app.route('/dps/<public_id>', methods=['GET'])
def get_one_dp(public_id: str):
    d = Dp.query.filter_by(public_id=public_id).first()
    if not d:
        return jsonify({'message': 'Dp não encontrada'})

    obj = {}
    obj = dp_to_json(d)
    return jsonify({'dp': obj})

# Cria uma DP
@app.route('/dps', methods=['POST'])
def create_dp():
    data = request.get_json()
    new_dp = Dp()
    new_dp = json_to_dp(data, str(uuid.uuid4()))
    db.session.add(new_dp)
    db.session.commit()
    db.session.flush()
    return jsonify({'message': 'Dp adicionada!', 'public_id': new_dp.public_id})

# Atualiza uma DP
@app.route('/dps/<public_id>', methods=['PUT'])
def update_dp(public_id: str):
    data = request.get_json()
    d = Dp.query.filter_by(public_id=public_id).first()
    if not d:
        return jsonify({'message': 'Dp não encontrada'})
    d.nome = data['nome']

    db.session.commit()
    return jsonify({'message': 'Dp atualizada'})

# Apaga uma DP
@app.route('/dps/<public_id>', methods=['DELETE'])
def delete_dp(public_id: str):
    return ''
# Retorna todas as ocorrências
@app.route('/ocorrencias', methods=['GET'])
def get_all_ocorrencias():
    ocorrencias = []
    placa = request.args.get('placa')
    if not placa:
        placa = ''
    numeroMotor = request.args.get('numeroMotor')
    if not numeroMotor:
        numeroMotor = ''
    chassis = request.args.get('chassis')
    if not chassis:
        chassis = ''
    situacao = request.args.get('situacao')
    if not situacao:
        ocorrencias = db.session.query(Ocorrencia).join(Veiculo, Ocorrencia.veiculo).\
        filter(Veiculo.placa.like("%"+placa+"%")).\
        filter(Veiculo.numeroMotor.like("%"+numeroMotor+"%")).\
        filter(Veiculo.chassis.like("%"+chassis+"%"))
    else:
        ocorrencias = db.session.query(Ocorrencia).join(Veiculo, Ocorrencia.veiculo).\
        filter(Veiculo.placa.like("%"+placa+"%")).\
        filter(Veiculo.numeroMotor.like("%"+numeroMotor+"%")).\
        filter(Veiculo.chassis.like("%"+chassis+"%")).\
        filter(Ocorrencia.situacao=='PENDENTE')
    print(placa)
    # ocorrencias = Ocorrencia.query.filter_by(Ocorrencia.veiculo.placa.like("%"+placa+"%")).all()



    output = []

    for ocorrencia in ocorrencias:
        oc_data = {}
        oc_data = ocorrencia_to_json(ocorrencia, ocorrencia.veiculo, ocorrencia.dp)
        output.append(oc_data)
    return jsonify({'ocorrencias':output})

# Retorna uma ocorrência específica
@app.route('/ocorrencias/<public_id>', methods=['GET'])
def get_one_ocorrencia(public_id: str):
    oc = Ocorrencia.query.filter_by(public_id=public_id).first()
    if not oc:
        return jsonify({'message': 'Ocorrencia nao encontrada'})
    obj = {}
    obj = ocorrencia_to_json(oc, oc.veiculo, oc.dp)
    return jsonify({'ocorrencia': obj})

# Cria uma ocorrência
@app.route('/ocorrencias', methods=['POST'])
def create_ocorrencia():
    ocorrencia = request.get_json()
    veiculo = Veiculo.query.filter_by(public_id=ocorrencia['veiculo']['public_id']).first()
    dp = Dp.query.filter_by(public_id=ocorrencia['dp']['public_id']).first()
    ocorrencia['dp_id'] = dp.id
    ocorrencia['veiculo_id'] = veiculo.id

    if((not veiculo) or (not dp)):
        return jsonify({'message': 'Veiculo ou DP nao especificado'})


    new_ocorrencia = json_to_ocorrencia(ocorrencia, str(uuid.uuid4()))
    db.session.add(new_ocorrencia)
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'ocorrencia criada', 'public_id': new_ocorrencia.public_id})

# Atualiza uma ocorrência
@app.route('/ocorrencias/<public_id>', methods=['PUT'])
def update_ocorrencia(public_id: str):
    ocorrencia = request.get_json()
    oc = Ocorrencia()
    veiculo = Veiculo.query.filter_by(public_id=ocorrencia['veiculo']['public_id']).first()
    dp = Dp.query.filter_by(public_id=ocorrencia['dp']['public_id']).first()
    if((not veiculo) or (not dp)):
        return jsonify({'message': 'Veiculo ou DP não encontrados'})
    oc = Ocorrencia.query.filter_by(public_id=public_id).first()

    if not oc:
        return jsonify({'message': 'Ocorrencia nao encontrada'})
    oc.tipoOcorrencia = ocorrencia['tipoOcorrencia']
    oc.situacao = ocorrencia['situacao']
    oc.numeroOcorrencia = ocorrencia['numeroOcorrencia']
    oc.localOcorrencia = ocorrencia['localOcorrencia']
    oc.data = datetime.strptime(ocorrencia['data'],'%Y-%m-%d').date()
    oc.observacoes = data['observacoes']
    oc.veiculo_id = veiculo.id
    oc.dp_id = dp.id
    db.session.flush()
    db.session.commit()

    return jsonify({'message': 'Ocorrencia atualizada'})


# Helper Methods

# Traduz uma ocorrencia para JSON
def ocorrencia_to_json(ocorrencia:Ocorrencia, veiculo:Veiculo, dp: Dp):
    obj = {}
    obj['public_id'] = ocorrencia.public_id
    obj['dp'] = dp_to_json(dp)
    obj['tipoOcorrencia'] = ocorrencia.tipoOcorrencia
    obj['situacao'] = ocorrencia.situacao
    obj['veiculo'] = veiculo_to_json(veiculo)
    obj['data']= ocorrencia.data
    obj['numeroOcorrencia'] = ocorrencia.numeroOcorrencia
    obj['localOcorrencia'] = ocorrencia.localOcorrencia
    obj['observacoes'] = ocorrencia.observacoes
    return obj

# Traduz um JSON para uma ocorrência
def json_to_ocorrencia(ocorrencia: {}, _uuid:str):
    obj = Ocorrencia()

    obj.tipoOcorrencia = ocorrencia['tipoOcorrencia']
    obj.situacao = ocorrencia['situacao']
    obj.veiculo_id = ocorrencia['veiculo_id']
    obj.dp_id = ocorrencia['dp_id']
    obj.numeroOcorrencia = ocorrencia['numeroOcorrencia']
    localOcorrencia = ocorrencia['localOcorrencia']
    obj.data = datetime.strptime(ocorrencia['data'],'%Y-%m-%d').date()
    obj.observacoes = ocorrencia['observacoes']

    if((_uuid != None)):
        obj.public_id = _uuid

    return obj

# Traduz um veículo para JSON
def veiculo_to_json(veiculo:Veiculo):
    obj = {}
    obj['public_id'] = veiculo.public_id
    obj['placa'] = veiculo.placa
    obj['chassis'] = veiculo.chassis
    obj['numeroMotor'] = veiculo.numeroMotor
    obj['cor'] = veiculo.cor
    obj['proprietario'] = proprietario_to_json(veiculo.proprietario)
    obj['tipo'] = veiculo.tipo
    obj['ano'] = veiculo.ano

    return obj

# Traduz um JSON para um veículo
def json_to_veiculo(data: {}, _uuid:str):
    new_veiculo = Veiculo()

    new_veiculo.placa=data['placa']
    new_veiculo.chassis=data['chassis']
    new_veiculo.numeroMotor=data['numeroMotor']
    new_veiculo.cor=data['cor']
    new_veiculo.proprietario_id=data['proprietario_id']
    new_veiculo.tipo=data['tipo']
    new_veiculo.ano=data['ano']

    if((_uuid != None)):
        new_veiculo.public_id=_uuid

    return new_veiculo

# Traduz uma DP para JSOn
def dp_to_json(dp: Dp):
    obj = {}
    obj['public_id'] = dp.public_id
    obj['nome'] = dp.nome
    return obj

# Traduz um JSON para uma DP
def json_to_dp(data: {}, _uuid: str):
    dp = Dp()

    dp.nome = data['nome']
    if((_uuid != None)):
        dp.public_id=_uuid
    return dp

# Traduz um Proprietario para JSON
def proprietario_to_json(prop: Proprietario):
    obj = {}
    obj['public_id'] = prop.public_id
    obj['nome'] = prop.nome
    obj['contato'] = prop.contato
    return obj

# Traduz um JSON para um Proprietário
def json_to_proprietario(data: {}, _uuid: str):
    prop = Proprietario()

    prop.nome = data['nome']
    prop.contato = data['contato']
    if((_uuid!= None)):
        prop.public_id = _uuid
    return prop

if __name__ == '__main__':
    app.run(debug=True)
