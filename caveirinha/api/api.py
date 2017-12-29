from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import uuid
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/itsadeadh2/Develop/flask/api/cav.db'

db = SQLAlchemy(app)

class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    placa = db.Column(db.String(8))
    chassis = db.Column(db.String(120))
    numeroMotor = db.Column(db.String(15))
    cor = db.Column(db.String(50))
    tipoVeiculo = db.Column(db.String(50))
    descricao = db.Column(db.String(450))
    nomeProprietario = db.Column(db.String(450))
    telefoneProprietario = db.Column(db.String(80))

class Dp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(120))

class Ocorrencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    rua = db.Column(db.String(250))
    bairro = db.Column(db.String(250))
    numero = db.Column(db.String(250))
    dp_id = db.Column(db.Integer, db.ForeignKey('dp.id'), nullable=False)
    dp = db.relationship('Dp', uselist=False, backref=db.backref('ocorrencias', lazy=True))
    tipoOcorrencia = db.Column(db.String(50))
    situacao = db.Column(db.String(50))
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    veiculo = db.relationship('Veiculo',uselist=False, backref=db.backref('ocorrencias', lazy=True))


@app.route('/veiculo', methods=['GET'])
def get_all_veiculos():
    veiculos = Veiculo.query.all()

    output = []

    for v in veiculos:
        obj = {}
        obj = veiculo_to_json(v)
        output.append(obj)
    return jsonify({'veiculos': output})

@app.route('/veiculo/<public_id>', methods=['GET'])
def get_one_veiculo(public_id: str):
    v = Veiculo.query.filter_by(public_id=public_id).first()

    if not v:
        return jsonify({'message': 'Veiculo nao encontrado.'})

    obj = {}
    obj = veiculo_to_json(v)
    return jsonify({'veiculo': obj})

@app.route('/veiculo', methods=['POST'])
def create_veiculo():
    data = request.get_json()
    new_veiculo = Veiculo()
    new_veiculo = json_to_veiculo(data,str(uuid.uuid4()))
    db.session.add(new_veiculo)
    db.session.commit()

    return jsonify({'message': 'Veiculo adicionado!'})

@app.route('/veiculo/<public_id>', methods=['PUT'])
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

@app.route('/veiculo/<public_id>', methods=['DELETE'])
def delete_veiculo(public_id: str):
    data = request.get_json()
    v = Veiculo.query.filter_by(public_id=public_id).first()

    if not v:
        return jsonify({'message': 'Veiculo nao encontrado.'})
    db.session.delete(v)
    db.session.commit()
    return jsonify({'message': 'Veiculo deletado'})

@app.route('/dp', methods=['GET'])
def get_all_dps():
    dps = Dp.query.all()

    output = []

    for d in dps:
        obj = {}
        obj = dp_to_json(d)
        output.append(obj)
    return jsonify({'dps': output})

@app.route('/dp/<public_id>', methods=['GET'])
def get_one_dp(public_id: str):
    d = Dp.query.filter_by(public_id=public_id).first()
    if not d:
        return jsonify({'message': 'Dp não encontrada'})

    obj = {}
    obj = dp_to_json(d)
    return jsonify({'dp': obj})

@app.route('/dp', methods=['POST'])
def create_dp():
    data = request.get_json()
    new_dp = Dp()
    new_dp = json_to_dp(data, str(uuid.uuid4()))
    db.session.add(new_dp)
    db.session.commit()
    return jsonify({'message': 'Dp adicionada!'})

@app.route('/dp/<public_id>', methods=['PUT'])
def update_dp(public_id: str):
    data = request.get_json()
    d = Dp.query.filter_by(public_id=public_id).first()
    if not d:
        return jsonify({'message': 'Dp não encontrada'})
    d.nome = data['nome']

    db.session.commit()
    return jsonify({'message': 'Dp atualizada'})

@app.route('/dp/<public_id>', methods=['DELETE'])
def delete_dp(public_id: str):
    return ''

@app.route('/ocorrencias', methods=['GET'])
def get_all_ocorrencias():
    ocorrencias = Ocorrencia.query.options(joinedload('veiculo'))

    output = []

    for ocorrencia in ocorrencias:
        oc_data = {}
        oc_data = ocorrencia_to_json(ocorrencia, ocorrencia.veiculo, ocorrencia.dp)
        output.append(oc_data)
    return jsonify({'ocorrencias':output})

@app.route('/ocorrencias/<public_id>', methods=['GET'])
def get_one_ocorrencia(public_id: str):
    oc = Ocorrencia.query.filter_by(public_id=public_id).first()
    if not oc:
        return jsonify({'message': 'Ocorrencia nao encontrada'})
    obj = {}
    obj = ocorrencia_to_json(oc, oc.veiculo, oc.dp)
    return jsonify({'ocorrencia': obj})

@app.route('/ocorrencias', methods=['POST'])
def create_ocorrencia():
    data = request.get_json()
    new_ocorrencia = json_to_ocorrencia(data, str(uuid.uuid4()))
    db.session.add(new_ocorrencia)
    db.session.commit()
    return jsonify({'message': 'ocorrencia criada'})

@app.route('/ocorrencias/<public_id>', methods=['PUT'])
def update_ocorrencia(public_id: str):
    data = request.get_json()
    print(data)
    oc = Ocorrencia()
    oc = Ocorrencia.query.filter_by(public_id=public_id).first()
    if not oc:
        return jsonify({'message': 'Ocorrencia nao encontrada'})
    oc.rua = data['rua']
    oc.bairro = data['bairro']
    oc.numero = data['numero']

    # oc.dp = json_to_dp(data['dp'],None)
    oc.tipoOcorrencia = data['tipoOcorrencia']
    oc.situacao = data['situacao']
    # oc.veiculo = json_to_veiculo(data['veiculo'], None)
    # _v = data['veiculo']
    # _veiculo = Veiculo.query.filter_by(public_id=_v['public_id']).first()
    # oc.veiculo_id = _veiculo.id
    db.session.commit()

    return jsonify({'message': 'Ocorrencia atualizada'})

def ocorrencia_to_json(ocorrencia:Ocorrencia, veiculo:Veiculo, dp: Dp):
    obj = {}
    obj['public_id'] = ocorrencia.public_id
    obj['rua'] = ocorrencia.rua
    obj['bairro'] = ocorrencia.bairro
    obj['numero'] = ocorrencia.numero
    obj['dp'] = dp_to_json(dp)
    obj['tipoOcorrencia'] = ocorrencia.tipoOcorrencia
    obj['situacao'] = ocorrencia.situacao
    obj['veiculo'] = veiculo_to_json(veiculo)
    return obj

def json_to_ocorrencia(ocorrencia: {}, _uuid:str):
    obj = Ocorrencia()

    obj.rua = ocorrencia['rua']
    obj.bairro = ocorrencia['bairro']
    obj.numero = ocorrencia['numero']
    obj.tipoOcorrencia = ocorrencia['tipoOcorrencia']
    obj.situacao = ocorrencia['situacao']

    if(_uuid != None):
        obj.public_id = _uuid

    if(ocorrencia['veiculo'] != None):
        _veiculo = ocorrencia['veiculo']
        if 'public_id' in _veiculo:
            veiculo = Veiculo.query.filter_by(public_id=_veiculo['public_id']).first()
            obj.veiculo_id = veiculo.id
        else:
            obj.veiculo = json_to_veiculo(ocorrencia['veiculo'], None)
            obj.veiculo.public_id =  str(uuid.uuid4())


    if(ocorrencia['dp'] != None):
        _dp = ocorrencia['dp']
        if 'public_id' in _dp:
            dp = Dp.query.filter_by(public_id=_dp['public_id']).first()
            obj.dp_id = dp.id
        else:
            obj.dp = json_to_dp(_dp, None)
            obj.dp.public_id = str(uuid.uuid4())

    return obj

def veiculo_to_json(veiculo:Veiculo):
    obj = {}
    obj['public_id'] = veiculo.public_id
    obj['placa'] = veiculo.placa
    obj['chassis'] = veiculo.chassis
    obj['numeroMotor'] = veiculo.numeroMotor
    obj['cor'] = veiculo.cor
    obj['tipoVeiculo'] = veiculo.tipoVeiculo
    obj['descricao'] = veiculo.descricao
    obj['nomeProprietario'] = veiculo.nomeProprietario
    obj['telefoneProprietario'] = veiculo.telefoneProprietario
    return obj

def json_to_veiculo(data: {}, _uuid:str):
    new_veiculo = Veiculo()

    new_veiculo.placa=data['placa']
    new_veiculo.chassis=data['chassis']
    new_veiculo.numeroMotor=data['numeroMotor']
    new_veiculo.cor=data['cor']
    new_veiculo.tipoVeiculo=data['tipoVeiculo']
    new_veiculo.descricao=data['descricao']
    new_veiculo.nomeProprietario=data['nomeProprietario']
    new_veiculo.telefoneProprietario=data['telefoneProprietario']

    if(_uuid != None):
        new_veiculo.public_id=_uuid

    return new_veiculo

def dp_to_json(dp: Dp):
    obj = {}
    obj['public_id'] = dp.public_id
    obj['nome'] = dp.nome
    return obj

def json_to_dp(data: {}, _uuid: str):
    dp = Dp()

    dp.nome = data['nome']
    if(_uuid != None):
        dp.public_id=_uuid
    return dp



if __name__ == '__main__':
    app.run(debug=True)
