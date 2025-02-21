import os, json
from datetime import datetime
from django.conf import settings

# Library json actions
class Json:

    @classmethod
    # Create json file in disk
    def create(cls, file, data):

        # Write in disk
        with open(file, "w", encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            print("Json created:" , file)

    @classmethod
    # Delete json file in disk
    def delete(cls, id):
        try:

            # Create file path
            file = f'{id}.json'
            json = f'{settings.JSON_PATH}/matchs/{file}'

            # Validate if json file exist
            if os.path.exists(json):
                os.remove(json)
                print("Json removed:" , file)

        except Exception as e:
            print(f"Error try json file: {e}")

# Library format functions
class Format:

    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", 
            "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    @classmethod
    def number(self, input):
        
        return "{:,}".format(input).replace(',', '.')

    @classmethod
    def persentage(self, number, total):
        if number == total:
            return f"100%"
        else:
            return f"{(number / total) * 100:.1f}%"

    @classmethod
    def new_date(self, date):

        week_day = self.days[date.weekday()]
        day = date.day
        month = self.months[date.month - 1]
        year = date.year
        
        return f"{week_day} {day:02d} de {month}"

    @classmethod
    def new_datetime(self, datetime):

        week_day = self.days[datetime.weekday()]
        day = datetime.day
        month = self.months[datetime.month - 1]
        year = datetime.year
        time = datetime.strftime("%H:%M")

        return f"{day} de {month} del {year} a las {time} Hrs"

    @classmethod
    def new_time(self, time):

        new_time = str(time).split(':')
        return f"{new_time[0]}:{new_time[1]} Hrs"

    @classmethod
    def file_name(self, prefix='users', extension='csv'):

        # Obtiene la fecha y hora actual
        now = datetime.now()
        
        # Formatea la fecha y hora en el formato deseado
        formatted_datetime = now.strftime('%Y%m%d_%H%M%S')
        
        # Crea el nombre del archivo
        filename = f"{prefix}_{formatted_datetime}.{extension}"
        
        return filename

    @classmethod
    def age(self, birthday):
        
        # Obtener la fecha actual
        now = datetime.now()
        
        # Calcular la diferencia en años
        age = now.year - birthday.year
        
        # Ajustar si el cumpleaños aún no ha ocurrido este año
        if (now.month, now.day) < (birthday.month, birthday.day):
            age -= 1

        return age