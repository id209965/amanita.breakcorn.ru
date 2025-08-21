# 🚀 Cypress Testing - Quick Start

## Быстрый старт для тестирования видеоплеера

### 1. Установка зависимостей

```bash
# Установить Node.js зависимости
npm install

# Установить Cypress
npx cypress install
```

### 2. Запуск тестов

#### Интерактивный режим (рекомендуется для разработки)
```bash
# Открыть Cypress Test Runner
npm run cypress:open

# ИЛИ с Makefile
make -f Makefile.cypress cypress-open
```

#### Headless режим (для CI/автоматизации)
```bash
# Запустить все тесты
npm test

# Запустить по категориям
npm run test:unit
npm run test:integration  
npm run test:memory
npm run test:performance

# С Makefile
make -f Makefile.cypress test
make -f Makefile.cypress test-unit
```

### 3. Запуск с локальным сервером

```bash
# Автоматически запустить сервер и тесты
npm run test:local

# ИЛИ вручную
# Терминал 1:
python3 -m http.server 8000

# Терминал 2:
npm test
```

### 4. Docker (полностью изолированное тестирование)

```bash
# Запустить все тесты в Docker
docker-compose -f docker-compose.cypress.yml up cypress-tests

# Запустить конкретную категорию
docker-compose -f docker-compose.cypress.yml up cypress-unit
docker-compose -f docker-compose.cypress.yml up cypress-integration
```

### 5. Просмотр результатов

**Отчеты сохраняются в:**
- `cypress/reports/` - HTML отчеты
- `cypress/screenshots/` - Скриншоты при ошибках
- `cypress/videos/` - Видео тестов

### 6. Основные команды

```bash
# Различные браузеры
npm run test:chrome
npm run test:firefox
npm run test:edge

# С видимым браузером
npm run test:headed

# Только быстрые тесты
npm run test:unit

# Тесты производительности
npm run test:performance

# Lighthouse аудит
make -f Makefile.cypress lighthouse-audit
```

### 7. Отладка

```bash
# Интерактивная отладка
npx cypress open

# Подробные логи
DEBUG=cypress:* npm test

# Конкретный тест
npx cypress run --spec "cypress/e2e/unit/page-structure.cy.js"
```

---

## ⚡ Почему Cypress?

- **Быстрее** - выполняется в том же run loop что и приложение
- **Надежнее** - автоматические retry и ожидания
- **Лучше отладка** - time-travel, live reload, DevTools
- **Современнее** - native async/await, ES6+ синтаксис
- **Удобнее** - интерактивный Test Runner

## 📋 Что тестируется?

✅ Загрузка страницы и JavaScript  
✅ Функциональность видеоплеера  
✅ Управление памятью и утечки  
✅ Производительность и время отклика  
✅ Переходы между видео  
✅ Обработка ошибок  
✅ Кроссбраузерная совместимость  

**Подробная документация:** [README_TESTING_CYPRESS.md](README_TESTING_CYPRESS.md)
