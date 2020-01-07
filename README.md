# Pygame-Project

## Символы для построения уровня

">" - враг который будет бвигаться вправо  
"<" - враг который будет бвигаться влево  
"@" - основной игрок  

Названия файлов без расширения из папки data/textures/png/tiles можно указывать в построении уровня.
Имя файла будет соответствовать изображению

Пример:

На месте символа "a" на уровне нарисуется изображение:

![a.png](data/textures/png/tiles/a.png)

### Все символы

"!" - blade.png  
"$" - bush1.png  
"%" - bush2.png  
"^" - button.png  
":" - cell.png  
"&" - door.png  
"1" - flower1.png  
"2" - flower2.png  
"3" - flower3.png  
"4" - flower4.png
"5" - flower5.png  
"6" - heart.png  
"7" - key.png  
"8" - box1.png  
"9" - tree1.png  
"0" - tree2.png  
" " или "#" - пустое место уровня
"/" - Невидимая стена

## Добавление своих уровней

Внутри функции `select_level` необходино создать экземпляр `SelectLevelSprite(center_x, center_y, number_level)`

Далее нобходимо создать файл с именем состоящим из номера уровня с расширением .lvl в папке data/levels

## Изменение поведения разных объектов

Изменить поведение разных объектов уровня можно при помощи словаря `GAME_OBJECTS_DICT`.
Ключ является именем файла без расширения из папки data/textures/png/elements.  
Значение состоит из нескольких элементов:
1. Название файла из папки data/textures/png/elements
2. Словарь с его свойствами:
    1. Колизия (материальнось) объекта по отношению к игровым персонажам
    2. Смерть при столкновении (только при актовном втором пункте), отностися только к игроку
    3. Кортеж состоящий из ширины и высоты объекта в пикселях

Пример: `'8': ('box1.png', {'collided': True, 'collided_do_kill': False, 'size': (48, 48)}),`

## Добавление собственных объектов

Вы можете доавлять свои собственные объекты с тексурами. Для этого необходимо в папку data/textures/png/elements
добавить изображение в формате .png и доавить его описание в словарь `GAME_OBJECTS_DICT`.
Документация по пользованию словарем в пункте "Изменение поведения разных объектов"


## Особенности

- На уровне может быть только один игрок
- Спрайт врага не начнет двигаться до тех пор, пока его не захватит камера
- Основной размер всех объектов уровня равен 48x48 px
- Чем меньше на уровне объектов, там быстрее загрузится уровень