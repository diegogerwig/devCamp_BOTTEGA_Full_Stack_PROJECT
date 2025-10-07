"""
Script de migración automática para TimeTracer
Ejecutar antes de iniciar la aplicación
"""
import os
from sqlalchemy import create_engine, text

def migrate_database():
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("⚠️  No DATABASE_URL found, skipping migration")
        return
    
    # Ajustar URL para pg8000
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://', 1)
    elif DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔍 Verificando estructura de la tabla users...")
            
            # Verificar si existe la columna users_password
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'users_password'
            """))
            
            has_users_password = result.fetchone() is not None
            
            if not has_users_password:
                print("⚠️  Columna 'users_password' no existe")
                
                # Verificar si existe 'password'
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'password'
                """))
                
                has_password = result.fetchone() is not None
                
                if has_password:
                    print("✅ Renombrando 'password' a 'users_password'...")
                    conn.execute(text("ALTER TABLE users RENAME COLUMN password TO users_password"))
                    conn.commit()
                    print("✅ Migración completada!")
                else:
                    print("⚠️  No existe ni 'password' ni 'users_password'")
                    print("🔧 Creando columna 'users_password'...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN users_password VARCHAR(255)"))
                    conn.commit()
                    print("✅ Columna creada!")
            else:
                print("✅ La columna 'users_password' ya existe")
        
        engine.dispose()
        print("✅ Migración completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate_database()