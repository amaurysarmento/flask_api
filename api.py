from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from pkg_resources import require


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app) #define a api como api restful do flask


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
 
    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"


# reqparse -> valida os dados quando sao enviados pra api. Eh usado quando for pra criar novos usuarios
user_args = reqparse.RequestParser() # Permite adicionar e analisar vários argumentos no contexto de uma única solicitação.
user_args.add_argument('name', type=str, required=True, help="Nome nao pode ta em branco")
user_args.add_argument('email', type=str, required=True, help="Email nao pode ta em branco")


userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}


# 1o endpoint
class Users(Resource):
    @marshal_with(userFields) # pega o Json userFields pra ser usado no metodo GET. O @marshal_with retornara os dados em Json em formato serializado.
    def get(self):# esse get é o metodo http GET
        users = UserModel.query.all() #ta recuperando todos os usuarios do db
        return users # como não tem nenhum user no db no momento, vai aparecer um array vazio
    
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()# vai retornar a mensagem que coloquei nas linhas de codigo 24 e 25
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

# class pra eu usar o get, patch e delete em um usuario especifico
class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, 'User not found') # 404 quer dizer nao encontrado
        return user 

    @marshal_with(userFields)
    def patch(self, id):# faz alteraçoes ou atualiza partes em partes especificas de um recurso(email address, por exemplo)
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, 'User not found') # 404 quer dizer nao encontrado
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit() #salva as alteraçoes feitas no banco de dados
        return user 

    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, 'User not found') # 404 quer dizer nao encontrado
        db.session.delete(user) 
        db.session.commit() #salva as alteraçoes feitas no banco de dados
        user = UserModel.query.all()
        return user, 204 # 204 quer dizer que a operaçao de apagar foi bem sucedida
    

api.add_resource(Users, '/api/users/') # <- atribue a class Users pra essa url 
api.add_resource(User, '/api/users/<int:id>') # <int:id> esse id é o parametro pro argumento dentro do get(id) da class User() 

@app.route('/')
def home():
    return '<h1>Hello World</h1>'

if __name__ == '__main__':
    app.run(debug=True)