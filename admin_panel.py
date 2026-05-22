"""
Админ-панель для управления ботом и просмотра статистики
"""

import sqlite3
from datetime import datetime, timedelta
from tabulate import tabulate

class AdminPanel:
    def __init__(self, db_name="sales_bot.db"):
        self.db_name = db_name

    def get_all_purchases(self):
        """Получить все покупки"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.user_id, u.telegram_name, u.email, p.product_name,
                   p.price, p.status, p.created_at
            FROM purchases p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.created_at DESC
        ''')

        purchases = cursor.fetchall()
        conn.close()

        return purchases

    def get_statistics(self):
        """Получить статистику"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Всего пользователей
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]

        # Всего покупок
        cursor.execute('SELECT COUNT(*) FROM purchases')
        total_purchases = cursor.fetchone()[0]

        # Завершенных покупок
        cursor.execute("SELECT COUNT(*) FROM purchases WHERE status = 'completed'")
        completed_purchases = cursor.fetchone()[0]

        # Сумма всех покупок
        cursor.execute("SELECT SUM(price) FROM purchases WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0] or 0

        # За последние 24 часа
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM purchases WHERE status = 'completed' AND created_at > ?",
            (yesterday,)
        )
        recent_purchases = cursor.fetchone()[0]

        conn.close()

        return {
            'total_users': total_users,
            'total_purchases': total_purchases,
            'completed_purchases': completed_purchases,
            'pending_purchases': total_purchases - completed_purchases,
            'total_revenue': total_revenue,
            'recent_purchases_24h': recent_purchases,
        }

    def get_pending_purchases(self):
        """Получить неоплаченные покупки"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.user_id, u.telegram_name, u.email, p.product_name,
                   p.price, p.created_at
            FROM purchases p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.status = 'pending'
            ORDER BY p.created_at DESC
        ''')

        purchases = cursor.fetchall()
        conn.close()

        return purchases

    def print_dashboard(self):
        """Вывести дашборд в консоль"""
        stats = self.get_statistics()

        print("\n" + "="*50)
        print("📊 АДМИН-ПАНЕЛЬ - СТАТИСТИКА")
        print("="*50)
        print(f"\n👥 Всего пользователей: {stats['total_users']}")
        print(f"📦 Всего покупок: {stats['total_purchases']}")
        print(f"✅ Завершено: {stats['completed_purchases']}")
        print(f"⏳ В ожидании: {stats['pending_purchases']}")
        print(f"💰 Общий доход: {stats['total_revenue']} руб.")
        print(f"📈 За 24 часа: {stats['recent_purchases_24h']} покупок")
        print("\n" + "="*50 + "\n")

    def print_purchases_table(self):
        """Вывести таблицу покупок"""
        purchases = self.get_all_purchases()

        if not purchases:
            print("Нет покупок")
            return

        table_data = []
        for p in purchases:
            table_data.append([
                p['user_id'],
                p['telegram_name'],
                p['email'],
                p['product_name'],
                f"{p['price']} руб.",
                p['status'],
                p['created_at'][:10]
            ])

        headers = ["ID", "Юзер", "Email", "Продукт", "Цена", "Статус", "Дата"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def print_pending_purchases(self):
        """Вывести неоплаченные покупки"""
        purchases = self.get_pending_purchases()

        if not purchases:
            print("\n✅ Все покупки оплачены!\n")
            return

        print("\n⏳ ОЖИДАЮЩИЕ ОПЛАТЫ:")
        print("-" * 50)

        table_data = []
        for p in purchases:
            table_data.append([
                p['user_id'],
                p['telegram_name'],
                p['email'],
                f"{p['price']} руб.",
                p['created_at'][:10]
            ])

        headers = ["ID", "Юзер", "Email", "Сумма", "Дата"]
        print(tabulate(table_data, headers=headers, tablefmt="simple"))
        print()

    def export_csv(self, filename="purchases.csv"):
        """Экспортировать данные в CSV"""
        import csv

        purchases = self.get_all_purchases()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['User ID', 'Name', 'Email', 'Product', 'Price', 'Status', 'Date'])

            for p in purchases:
                writer.writerow([
                    p['user_id'],
                    p['telegram_name'],
                    p['email'],
                    p['product_name'],
                    p['price'],
                    p['status'],
                    p['created_at']
                ])

        print(f"✅ Данные экспортированы в {filename}")

if __name__ == "__main__":
    admin = AdminPanel()

    while True:
        print("\n" + "="*50)
        print("🛠️ АДМИН-ПАНЕЛЬ")
        print("="*50)
        print("1️⃣  Дашборд")
        print("2️⃣  Все покупки")
        print("3️⃣  Ожидающие оплату")
        print("4️⃣  Экспорт CSV")
        print("5️⃣  Выход")
        print("="*50)

        choice = input("Выбери опцию (1-5): ").strip()

        if choice == "1":
            admin.print_dashboard()

        elif choice == "2":
            admin.print_purchases_table()

        elif choice == "3":
            admin.print_pending_purchases()

        elif choice == "4":
            filename = input("Имя файла (default: purchases.csv): ").strip() or "purchases.csv"
            admin.export_csv(filename)

        elif choice == "5":
            print("Выход...")
            break

        else:
            print("❌ Неверная опция")

        input("\nНажми Enter для продолжения...")
