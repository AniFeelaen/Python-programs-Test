import pygame
import json
import os
import time

# Инициализация
pygame.init()
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космическая Стратегия")
FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 24)

# Цвета
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
ORANGE = (200, 150, 50)

# Загрузка данных планет
with open('planet_data.json', encoding='utf-8') as f:
    PLANET_DATA = json.load(f)['planets']

# Типы кораблей
SHIP_TYPES = {
    "light": {"power": 1, "hp": 10, "cost": {"metal": 20, "fuel": 10}},
    "medium": {"power": 3, "hp": 25, "cost": {"metal": 50, "fuel": 30}},
    "heavy": {"power": 5, "hp": 50, "cost": {"metal": 100, "fuel": 60}}
}

# Исследования
TECHNOLOGIES = {
    "medium_ship": {"unlocked": False, "cost": {"metal": 150, "fuel": 100}, "desc": "Открывает постройку средних кораблей"},
    "fuel_efficiency": {"unlocked": False, "cost": {"metal": 100, "fuel": 80}, "desc": "Уменьшает потребление топлива"},
    "laser_weapon": {"unlocked": False, "cost": {"metal": 200, "fuel": 150}, "desc": "Увеличивает мощность всех кораблей"},
    "quantum_core": {"unlocked": False, "cost": {"metal": 350, "fuel": 200}, "desc": "Увеличивает добычу металла"},
    "bio_reactor": {"unlocked": False, "cost": {"metal": 180, "fuel": 120}, "desc": "Увеличивает добычу топлива"},
    "stealth_tech": {"unlocked": False, "cost": {"metal": 300, "fuel": 150}, "desc": "Увеличивает шанс захвата"},
    "advanced_engine": {"unlocked": False, "cost": {"metal": 250, "fuel": 200}, "desc": "Ускоряет движение кораблей"},
}

# Постройки
BUILDING_TYPES = {
    "Mine": {
        "level": 1,
        "base_gain": 1.0,
        "cost": {"metal": 50, "fuel": 20},
        "multiplier": 1.5
    },
    "Refinery": {
        "level": 1,
        "base_gain": 0.5,
        "cost": {"metal": 40, "fuel": 30},
        "multiplier": 1.5
    },
    "Shipyard": {
        "level": 1,
        "ship_speed": 0.1,
        "cost": {"metal": 70, "fuel": 50},
        "multiplier": 1.5
    },
    "Lab": {
        "level": 1,
        "research_speed": 0.05,
        "cost": {"metal": 100, "fuel": 80},
        "multiplier": 1.5
    }
}

# --- Загрузка изображений ---
ASSET_PATH = 'assets'

def load_image(name, size=None):
    path = os.path.join(ASSET_PATH, name)
    img = pygame.image.load(path)
    if size:
        img = pygame.transform.scale(img, size)
    return img

PLANET_IMAGES = {
    "Землеподобная": load_image("terra.png", (64, 64)),
    "Ледяная": load_image("icy.png", (64, 64)),
    "Огненная": load_image("fire.png", (64, 64)),
    "Дикий мир": load_image("wild.png", (64, 64)),
    "Газовый гигант": load_image("gas_giant.png", (64, 64)),
    "Разрушенная": load_image("destroyed.png", (64, 64)),
    "Цветущая": load_image("blooming.png", (64, 64)),
    "Тёмная": load_image("dark.png", (64, 64)),
    "Пепельная": load_image("ash.png", (64, 64)),
    "Энергетическая": load_image("energy.png", (64, 64))
}

SHIP_IMAGES = {
    "light": load_image("ship_light.png", (48, 48)),
    "medium": load_image("ship_medium.png", (48, 48)),
    "heavy": load_image("ship_heavy.png", (48, 48))
}

BACKGROUND = load_image("background.png", (WIDTH, HEIGHT))

# Вкладка экрана
SCREEN_STATE = "Status"

class Planet:
    def __init__(self, data):
        self.name = data["name"]
        self.type = data["type"]
        self.base_metal_gain = data["base_metal_gain"]
        self.base_fuel_gain = data["base_fuel_gain"]
        self.tech_unlock = data["tech_unlock"]
        self.defense = data["defense"]
        self.is_captured = False
        self.buildings = {name: data.copy() for name, data in BUILDING_TYPES.items()}

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.metal = 100
        self.fuel = 50
        self.ships = {"light": 5, "medium": 0, "heavy": 0}
        self.planets = [Planet(p) for p in PLANET_DATA]
        self.captured_planets = [self.planets[0]]
        self.planets[0].is_captured = True
        self.technologies = {k: v.copy() for k, v in TECHNOLOGIES.items()}
        self.last_tick = time.time()
        self.boss_defeated = False
        self.final_boss = {
            "name": "Центральная звезда",
            "defense": {"light": 20, "medium": 10, "heavy": 5}
        }

        self.load_save()

    def draw_text(self, text, x, y, color=WHITE, font=FONT):
        label = font.render(text, True, color)
        SCREEN.blit(label, (x, y))

    def draw_button(self, text, x, y, w, h, color, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + w and y < mouse[1] < y + h:
            pygame.draw.rect(SCREEN, (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255)), (x, y, w, h))
            if click[0] == 1 and action:
                action()
        else:
            pygame.draw.rect(SCREEN, color, (x, y, w, h))
        self.draw_text(text, x + 10, y + 10)

    def attack_planet(self, planet):
        if planet.is_captured:
            return
        total_power = sum(self.ships[t] * SHIP_TYPES[t]["power"] for t in self.ships)
        enemy_power = sum(planet.defense[t] * SHIP_TYPES[t]["power"] for t in planet.defense)
        if total_power > enemy_power:
            planet.is_captured = True
            self.captured_planets.append(planet)
            if planet.tech_unlock:
                self.technologies[planet.tech_unlock]["unlocked"] = True
            self.save_progress()
            messagebox(f"Планета {planet.name} захвачена!")
        else:
            lost = int(sum(self.ships.values()) * 0.3)
            while lost > 0:
                for t in self.ships:
                    if self.ships[t] > 0:
                        self.ships[t] -= 1
                        lost -= 1
                        if lost <= 0:
                            break
            messagebox(f"Неудачная атака на {planet.name}")

    def build_ship(self, stype):
        cost = SHIP_TYPES[stype]["cost"]
        if self.metal >= cost["metal"] and self.fuel >= cost["fuel"]:
            self.metal -= cost["metal"]
            self.fuel -= cost["fuel"]
            self.ships[stype] += 1
            self.save_progress()

    def research_tech(self, tech):
        if self.technologies[tech]["unlocked"]:
            return
        req = self.technologies[tech]["cost"]
        if self.metal >= req["metal"] and self.fuel >= req["fuel"]:
            self.metal -= req["metal"]
            self.fuel -= req["fuel"]
            self.technologies[tech]["unlocked"] = True
            self.save_progress()
            messagebox(f"Исследование '{tech}' завершено!")

    def update_resources(self):
        now = time.time()
        delta = now - self.last_tick
        if delta >= 1:
            metal_inc = sum(
                p.base_metal_gain * p.buildings["Mine"]["level"] for p in self.captured_planets
            )
            fuel_inc = sum(
                p.base_fuel_gain * p.buildings["Refinery"]["level"] for p in self.captured_planets
            )
            self.metal += metal_inc * delta
            self.fuel += fuel_inc * delta
            self.last_tick = now

    def upgrade_building(self, building_name):
        planet = self.captured_planets[0]
        current = planet.buildings[building_name]
        if self.metal >= current["cost"]["metal"] and self.fuel >= current["cost"]["fuel"]:
            self.metal -= current["cost"]["metal"]
            self.fuel -= current["cost"]["fuel"]
            current["level"] += 1
            next_cost = {
                "metal": int(current["cost"]["metal"] * current["multiplier"]),
                "fuel": int(current["cost"]["fuel"] * current["multiplier"])
            }
            planet.buildings[building_name]["cost"] = next_cost
            self.save_progress()

    def run(self):
        while self.running:
            SCREEN.blit(BACKGROUND, (0, 0))
            self.update_resources()

            # Кнопки вкладок
            self.draw_button("Статус", 20, 650, 150, 40, GRAY, lambda: self.set_screen("Status"))
            self.draw_button("Планета", 180, 650, 150, 40, GREEN, lambda: self.set_screen("Planet"))
            self.draw_button("Галактика", 340, 650, 150, 40, BLUE, lambda: self.set_screen("Galaxy"))
            self.draw_button("Исследования", 500, 650, 150, 40, (100, 100, 200), lambda: self.set_screen("Research"))
            self.draw_button("Верфь", 660, 650, 150, 40, (100, 100, 100), lambda: self.set_screen("Shipyard"))
            self.draw_button("New Game+", 820, 650, 150, 40, ORANGE, self.new_game_plus)

            # Отрисовка текущего экрана
            if SCREEN_STATE == "Status":
                self.draw_status_screen()
            elif SCREEN_STATE == "Planet":
                self.draw_planet_screen()
            elif SCREEN_STATE == "Galaxy":
                self.draw_galaxy_screen()
            elif SCREEN_STATE == "Research":
                self.draw_research_screen()
            elif SCREEN_STATE == "Shipyard":
                self.draw_shipyard_screen()

            self.check_victory()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()
            self.clock.tick(30)

    def draw_status_screen(self):
        self.draw_text(f"Металл: {int(self.metal)}", 20, 20)
        self.draw_text(f"Топливо: {int(self.fuel)}", 20, 50)
        self.draw_text("Корабли:", 20, 80)
        y = 110
        for s, cnt in self.ships.items():
            SCREEN.blit(SHIP_IMAGES[s], (20, y))
            self.draw_text(f"{s.capitalize()}: {cnt}", 70, y + 10)
            y += 60

    def draw_planet_screen(self):
        planet = self.captured_planets[0]
        y = 20
        for building_name, data in planet.buildings.items():
            cost = data["cost"]
            self.draw_button(
                f"{building_name} Уровень {data['level']} ({cost['metal']}/{cost['fuel']})",
                600, y, 350, 40, GRAY,
                lambda b=building_name: self.upgrade_building(b)
            )
            y += 50

    def draw_galaxy_screen(self):
        y = 20
        for p in self.planets:
            color = GREEN if p.is_captured else RED
            text = f"[{p.name}] {p.type} - Защита: {p.defense}"
            self.draw_button(text, 20, y, 700, 40, color, lambda pl=p: self.attack_planet(pl))
            y += 50

    def draw_research_screen(self):
        y = 20
        for tech, data in self.technologies.items():
            if not data["unlocked"]:
                cost = data["cost"]
                self.draw_button(f"{tech} ({cost['metal']}/{cost['fuel']})", 20, y, 400, 40, BLUE, lambda t=tech: self.research_tech(t))
            else:
                self.draw_text(f"[Изучено] {tech}", 20, y)
            y += 50

    def draw_shipyard_screen(self):
        y = 20
        for s in SHIP_TYPES:
            unlocked = True
            if s == "medium" and not self.technologies["medium_ship"]["unlocked"]:
                unlocked = False
            if s == "heavy" and not self.technologies.get("heavy_ship", {"unlocked": False})["unlocked"]:
                unlocked = False
            if unlocked:
                cost = SHIP_TYPES[s]["cost"]
                self.draw_button(f"Строить {s} ({cost['metal']}/{cost['fuel']})", 20, y, 300, 40, GREEN, lambda st=s: self.build_ship(st))
            else:
                self.draw_text(f"{s.capitalize()} (заблокирован)", 20, y)
            y += 50

    def set_screen(self, screen):
        global SCREEN_STATE
        SCREEN_STATE = screen

    def save_progress(self):
        data = {
            "metal": self.metal,
            "fuel": self.fuel,
            "ships": self.ships,
            "captured_planets": [p.name for p in self.captured_planets],
            "technologies": {t: d["unlocked"] for t, d in self.technologies.items()},
            "buildings": {
                p.name: {b: p.buildings[b]["level"] for b in p.buildings}
                for p in self.captured_planets
            },
            "boss_defeated": self.boss_defeated
        }
        with open("save.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_save(self):
        try:
            with open("save.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.metal = data.get("metal", 100)
            self.fuel = data.get("fuel", 50)
            self.ships = data.get("ships", {"light": 5, "medium": 0, "heavy": 0})
            captured_names = data.get("captured_planets", ["Терра"])

            for p in self.planets:
                if p.name in captured_names:
                    p.is_captured = True

            tech_data = data.get("technologies", {})
            for t in self.technologies:
                self.technologies[t]["unlocked"] = tech_data.get(t, False)

            building_data = data.get("buildings", {})
            for p in self.captured_planets:
                if p.name in building_data:
                    for b in building_data[p.name]:
                        level = building_data[p.name][b]
                        p.buildings[b]["level"] = level
                        p.buildings[b]["cost"] = {
                            "metal": int(BUILDING_TYPES[b]["cost"]["metal"] * (BUILDING_TYPES[b]["multiplier"] ** (level - 1))),
                            "fuel": int(BUILDING_TYPES[b]["cost"]["fuel"] * (BUILDING_TYPES[b]["multiplier"] ** (level - 1)))
                        }

            self.boss_defeated = data.get("boss_defeated", False)

        except FileNotFoundError:
            print("Файл сохранения не найден. Запуск с начальными данными.")
        except json.JSONDecodeError:
            print("Ошибка чтения файла сохранения. Возможно, файл повреждён.")

    def check_victory(self):
        if len(self.captured_planets) == len(self.planets) and not self.boss_defeated:
            self.show_final_boss()

    def show_final_boss(self):
        total_power = sum(self.ships[t] * SHIP_TYPES[t]["power"] for t in self.ships)
        boss_power = sum(self.final_boss["defense"][t] * SHIP_TYPES[t]["power"] for t in self.final_boss["defense"])

        if total_power > boss_power:
            self.boss_defeated = True
            messagebox("ПОБЕДА! Вы захватили всю галактику!")
        else:
            messagebox("Вы проиграли финальному боссу.")

    def new_game_plus(self):
        self.metal = 200
        self.fuel = 100
        self.ships = {"light": 10, "medium": 2, "heavy": 1}
        self.boss_defeated = False

        for p in self.planets:
            for key in p.defense:
                p.defense[key] = int(p.defense[key] * 1.5)

        self.final_boss["defense"]["heavy"] += 2
        self.save_progress()
        messagebox("Новый раунд начался! Все стало сложнее...")

def messagebox(msg):
    print(msg)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()