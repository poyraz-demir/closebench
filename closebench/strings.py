"""Локали пользовательских строк. Строки НЕ трогают генератор случайных чисел:
для одного seed миры ru и en совпадают по всем числам, отличается только текст.

T(lang, key, **fmt) — единственная точка входа. Все шаблоны форматируются через
str.format, поэтому литеральные фигурные скобки в шаблонах удвоены."""
from __future__ import annotations

LANGS = ("ru", "en")

_MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def month_label(lang: str, m: int) -> str:
    """Подпись месяца в тексте: ru — «11», en — «Nov»."""
    return _MONTHS_EN[m - 1] if lang == "en" else f"{m:02d}"

RU = {
    "company": "ООО «Ридж»",

    # --- план счетов ---
    "coa.1000": "Расчётный счёт",
    "coa.1100": "Дебиторская задолженность",
    "coa.1200": "Запасы",
    "coa.1300": "Расходы будущих периодов",
    "coa.1500": "Основные средства",
    "coa.1590": "Накопленная амортизация",
    "coa.2000": "Кредиторская задолженность",
    "coa.2100": "Начисленные обязательства",
    "coa.2200": "Зарплата к выплате",
    "coa.2300": "НДС к уплате",
    "coa.2400": "Доходы будущих периодов",
    "coa.2500": "Межкомпанийные расчёты",
    "coa.3000": "Уставный капитал",
    "coa.3100": "Нераспределённая прибыль",
    "coa.4000": "Выручка",
    "coa.5000": "Себестоимость",
    "coa.6000": "Зарплата",
    "coa.6100": "Аренда",
    "coa.6200": "Электроэнергия и коммунальные",
    "coa.6300": "Профессиональные услуги",
    "coa.6400": "Амортизация",
    "coa.6500": "Программное обеспечение",
    "coa.6600": "Связь и охрана",
    "coa.6700": "Курсовые разницы",
    "coa.6800": "Страхование",
    "coa.6900": "Прочие расходы",

    # --- стартовые проводки ---
    "je.founder": "Взнос учредителя",
    "je.opening_stock": "Закупка складского запаса",
    "je.equipment": "Покупка оборудования",
    "je.insurance_policy": "Страховой полис на год",

    # --- обычный месяц ---
    "je.revenue": "Выручка за {m:02d}.{y}",
    "je.goods_received": "Поступление товара {m:02d}.{y}",
    "je.cogs": "Себестоимость за {m:02d}.{y}",
    "je.customer_receipts": "Поступление от клиентов {m:02d}",
    "je.supplier_payment": "Оплата поставщикам товара {m:02d}",
    "je.rent": "Аренда {m:02d}.{y}",
    "je.payroll": "Зарплата {m:02d}.{y}",
    "je.payroll_accrual": "Резерв по зарплате {m:02d}.{y}",
    "je.electricity": "Электроэнергия {m:02d}.{y}",
    "je.telecom": "Связь и охрана {m:02d}.{y}",
    "je.insurance_amort": "Списание страховки {m:02d}.{y}",
    "je.depreciation": "Амортизация {m:02d}.{y}",
    "doc.util.title": "Счёт за электроэнергию, {m:02d}.{y}, ООО «Энергосбыт»",
    "doc.util.body": "Период: {m:02d}.{y}\nТариф: коммерческий C2\nПотреблено: {kwh} кВт·ч\nК оплате: {util}.00",
    "vendor.util": "Энергосбыт",

    # --- E1 unrecorded_invoice ---
    "doc.sub.title": "Счёт подрядчика ООО «Ториум»",
    "doc.sub.body": "Акт выполненных работ за {m:02d}.{y}\nУслуги субподряда\nК оплате: {amt}.00\nДата акта: {date}",
    "doc.sub.body_decoy": "Акт выполненных работ за {m:02d}.{y}\nУслуги субподряда\nК оплате: {amt}.00",
    "vendor.torium": "Ториум",
    "je.sub_decoy": "Ториум, акт субподряда",
    "err.unrecorded_invoice": "Счёт подрядчика SUB на {amt} не проведён: занижены себестоимость и кредиторка",

    # --- E2 duplicate_invoice ---
    "memo.aud.plain": "Профуслуги, аудит (счёт AUD-114)",
    "memo.aud.terse": "Аудит-Про, сч. AUD-114",
    "memo.aud.terse2": "Аудит-Про, акт за 3 кв.",
    "doc.aud.title": "Счёт ООО «Аудит-Про» AUD-114",
    "doc.aud.body": "Аудиторские услуги за 3 квартал\nК оплате: {amt}.00\nНомер счёта: AUD-114",
    "vendor.audit": "Аудит-Про",
    "err.duplicate_invoice": "Счёт AUD-114 проведён дважды ({e1} и {e2}): завышены расходы и кредиторка на {amt}",

    # --- E3 capex_expensed ---
    "memo.hw.plain": "Закупка серверного оборудования",
    "memo.hw.terse": "Оплата сч. HW-7781 Техносклад",
    "doc.hw.title": "Счёт ООО «Техносклад» HW-7781",
    "doc.hw.body": "Серверное оборудование, срок полезного использования 5 лет\nСтоимость: {amt}.00\nОсновное средство, инв. номер ОС-114\nВвод в эксплуатацию: {y}-12-01",
    "doc.hw.body_decoy": "Серверное оборудование, срок полезного использования 5 лет\nСтоимость: {amt}.00\nОсновное средство, инв. номер ОС-114\nВвод в эксплуатацию: {y}-12-01 (в отчётном периоде не используется)",
    "vendor.hw": "Техносклад",
    "err.capex_expensed": "Оборудование на {amt} со сроком службы 5 лет списано в прочие расходы вместо ОС",

    # --- E4 prepaid_not_deferred ---
    "memo.sw.plain": "Лицензия ПО на 12 месяцев",
    "memo.sw.terse": "Софтлайн, сч. SW-900",
    "doc.sw.title": "Договор лицензии ПО SW-900",
    "doc.sw.body": "Срок: 12 месяцев с {date}\nСтоимость: {amt}.00\nОплата единовременно за весь срок",
    "doc.sw.body_decoy": "Срок: 1 месяц ({m:02d}.{y})\nСтоимость: {amt}.00\nОплата помесячно по факту.",
    "vendor.sw": "Софтлайн",
    "err.prepaid_not_deferred": "Годовая лицензия {amt} списана целиком; в периоде должно остаться {monthly}",

    # --- E5 revenue_cutoff ---
    "memo.adv.plain": "Аванс от клиента «Вектор»",
    "memo.adv.terse": "Поступление Вектор, дог. ADV-51",
    "doc.adv.title": "Договор с ООО «Вектор» ADV-51",
    "doc.adv.body": "Предоплата: {amt}.00\nПериод оказания услуг: январь–март {y1}\nУслуги в отчётном периоде не оказывались",
    "doc.adv.body_decoy": "Оплата: {amt}.00 за услуги, оказанные в {m:02d}.{y}\nАкт подписан {date}, выручка отражена ранее.",
    "customer.vector": "Вектор",
    "err.revenue_cutoff": "Аванс {amt} за услуги следующего года признан выручкой периода",

    # --- E6 unrecorded_bank_fee ---
    "err.unrecorded_bank_fee": "Комиссия банка {amt} есть в выписке, но не проведена",

    # --- E7 misclassified_expense (в ru «АР-77» исторически кириллицей; ref — латиница AR-77) ---
    "memo.ar.plain": "Оплата по договору аренды склада (АР-77)",
    "memo.ar.terse": "Складсервис, дог. АР-77",
    "doc.ar.title": "Договор аренды складского помещения АР-77",
    "doc.ar.body": "Предмет: аренда склада 400 кв. м\nАрендная плата за {m:02d}.{y}: {amt}.00\nТип: операционная аренда помещения",
    "doc.ar.body_decoy": "Предмет: аренда склада 400 кв. м\nАрендная плата за {m:02d}.{y}: {amt}.00",
    "vendor.ar": "Складсервис",
    "err.misclassified_expense": "Аренда склада {amt} отнесена на профуслуги (6300) вместо аренды (6100)",

    # --- E8 intercompany_mismatch ---
    "doc.ic.title": "Письмо от дочерней компании: сверка межкомпанийных расчётов",
    "doc.ic.body": "Коллеги, по нашим данным за {m:02d}.{y} мы оказали вам услуги на {amt}.00 (акт {ic}). В вашей оборотке этой суммы нет — просим отразить до закрытия на счёте межкомпанийных расчётов.",
    "doc.ic.body_decoy": "Коллеги, сверили расчёты за {m:02d}.{y}: расхождений нет, взаимных обязательств на конец периода не возникло.",
    "counterparty.subsidiary": "дочерняя компания",
    "err.intercompany_mismatch": "Межкомпанийные услуги {amt} не отражены: расхождение при консолидации",

    # --- E9, E13–E17: ошибки-отсутствия ---
    "err.missing_recurring": "Начисление «связь и охрана» {amt} отсутствует за {m:02d}.{y}; во всех прочих месяцах года оно есть",
    "err.depreciation_stopped": "Амортизация 4000 не начислена за {m:02d}.{y}; ряд DEP рвётся",
    "err.prepaid_amort_stopped": "Списание годовой страховки {amt} не проведено за {m:02d}.{y}; остаток РБП завышен",
    "err.accrual_not_released": "При выплате за {m:02d}.{y} резерв прошлого месяца {amt} не погашен: вся сумма ушла в расход, обязательство 2200 зависло",
    "err.inventory_receipt_gap": "Поступление товара за {m:02d}.{y} на {amt} не проведено, хотя себестоимость списана: запасы и кредиторка занижены",
    "err.payroll_cutoff": "Резерв по зарплате за {tail} дней ({amt}) не начислен за {m:02d}.{y}; во всех прочих месяцах начислялся",

    # --- E10 fx_revaluation ---
    "memo.nw.plain": "Импортная поставка, счёт в евро",
    "memo.nw.terse": "Nordwerk GmbH, инв. NW-2210",
    "je.nw_settle": "Погашение NW-2210",
    "doc.nw.title": "Инвойс Nordwerk GmbH NW-2210",
    "doc.nw.body": "Поставка комплектующих\nСумма: EUR {eur}.00\nУсловия оплаты: 60 дней\nНа дату поставки ({date}) обязательство пересчитано по курсу {r1}.\nНа конец периода задолженность не погашена.",
    "doc.nw.body_decoy": "Поставка комплектующих\nСумма: EUR {eur}.00\nОбязательство пересчитано по курсу {r1} и погашено {date} по тому же курсу.",
    "vendor.nw": "Nordwerk GmbH",
    "doc.fx.title": "Справка о курсах валют",
    "doc.fx.body": "Курс EUR на {date}: {r1}\nКурс EUR на {end}: {r2}\nНепогашенные валютные обязательства переоцениваются на отчётную дату.",
    "doc.fx.body_decoy": "Курс EUR на {date}: {r1}\nКурс EUR на {end}: {r1}\nНепогашенных валютных обязательств на отчётную дату нет.",
    "err.fx_revaluation": "Валютная кредиторка EUR {eur} не переоценена: курс вырос с {r1} до {r2}, разница {diff}",

    # --- E11 depreciation_prorata ---
    "memo.ml.plain": "Приобретение линии упаковки",
    "memo.ml.terse": "Оплата сч. ML-330 Мехлайн",
    "je.ml_dep_decoy": "Амортизация ОС-221 за {days} дн.",
    "doc.ml.title": "Счёт ООО «Мехлайн» ML-330",
    "doc.ml.body": "Линия упаковки, инв. номер ОС-221\nСтоимость: {amt}.00\nСрок полезного использования: 5 лет\nВведена в эксплуатацию: {date} (акт приёмки подписан)",
    "vendor.ml": "Мехлайн",
    "err.depreciation_prorata": "ОС {amt} введено {date}, амортизация за {days} дней ({dep}) не начислена",

    # --- E12 service_span_cutoff ---
    "memo.qb.plain": "Сопровождение проекта, 60 дней",
    "memo.qb.terse": "Кьюбит, дог. QB-88",
    "doc.qb.title": "Договор сопровождения QB-88 (ООО «Кьюбит»)",
    "doc.qb.body": "Период оказания услуг: с {start} по {end} (60 календарных дней)\nСтоимость: {amt}.00, оплата единовременно авансом\nУслуги оказываются равномерно в течение срока договора.",
    "doc.qb.body_decoy": "Период оказания услуг: с {start} по {end} (внутри отчётного периода)\nСтоимость: {amt}.00\nРаботы приняты полностью, акт подписан {end}.",
    "vendor.qb": "Кьюбит",
    "err.service_span_cutoff": "Договор QB-88 на {amt} за 60 дней списан целиком; в периоде {in_period} дней, к переносу {defer}",

    # --- законные ловушки ---
    "je.cs": "Клинсервис, сч. {n}",
    "doc.cs.title": "Счёт ООО «Клинсервис» {n}",
    "doc.cs.body": "Уборка помещений, {per} {m:02d}.{y}\nК оплате: {amt}.00\nДоговор предусматривает два акта в месяц.",
    "half.first": "первая половина",
    "half.second": "вторая половина",
    "vendor.cs": "Клинсервис",
    "je.pt": "Промтех, сч. PT-55",
    "doc.pt.title": "Счёт ООО «Промтех» PT-55",
    "doc.pt.body": "Расходные материалы и комплектующие (срок использования до 12 месяцев)\nК оплате: {amt}.00\nНе является основным средством: единица стоимостью менее лимита.",
    "vendor.pt": "Промтех",

    # --- учётная политика и выписка ---
    "doc.pol.title": "Учётная политика (выдержка)",
    "doc.pol.body": (
        "1. Амортизация начисляется линейно со дня ввода объекта в эксплуатацию "
        "включительно, пропорционально числу дней в месяце.\n"
        "2. Зарплата выплачивается 25-го числа за период с 1-го по 25-е; "
        "оставшиеся дни месяца (в {m:02d}.{y} — {tail} дн.) "
        "начисляются резервом на конец месяца и гасятся следующей выплатой.\n"
        "3. Расходы по договорам, срок которых пересекает конец периода, "
        "распределяются равномерно по календарным дням.\n"
        "4. Непогашенные обязательства в иностранной валюте переоцениваются "
        "по курсу на отчётную дату; разница относится на счёт курсовых разниц.\n"
        "5. Лимит признания основного средства: 50 000. Ниже лимита — расход периода.\n"
        "6. Расходы будущих периодов (страховой полис) списываются равными "
        "долями ежемесячно в течение срока полиса.\n"
        "7. Резерв по зарплате гасится ближайшей выплатой.\n"
        "8. Корректировки закрытия проводятся последним днём периода, включая "
        "исправление пропусков прошлых месяцев текущего года."),
    "doc.bank.title": "Выписка по счёту за {m:02d}.{y}",
    "doc.bank.body_nofee": "Остаток на конец периода по выписке: {bal}\nВсе движения периода отражены в учёте, расхождений нет.",
    "doc.bank.body_fee": "Остаток на конец периода по выписке: {bal}\nВ том числе списание: комиссия за обслуживание {fee}.00 ({date})",

    # --- ledger ---
    "ledger.no_lines": "проводка без строк",
    "ledger.unknown_account": "неизвестный счёт {account}",
    "ledger.negative": "отрицательные суммы запрещены",
    "ledger.both_sides": "строка не может быть и дебетом, и кредитом",
    "ledger.unbalanced": "не сходится: Дт {d} ≠ Кт {c}",

    # --- tools ---
    "tool.coa_header": "код  | наименование                        | тип",
    "tool.log.accounts": "{n} счетов",
    "tool.tb_header": "код  | счёт                              | дебет      | кредит",
    "tool.tb_total": "ИТОГО: Дт {d} | Кт {c} | {status}",
    "tool.balanced": "сходится",
    "tool.unbalanced": "НЕ СХОДИТСЯ",
    "tool.log.rows": "{n} строк",
    "tool.dr": "Дт",
    "tool.cr": "Кт",
    "tool.log.entries": "{n} проводок",
    "tool.empty": "(пусто)",
    "tool.log.no_account": "нет счёта",
    "tool.no_account": "счёта {code} нет в плане счетов. Посмотрите полный список: chart_of_accounts",
    "tool.balance": "{code} {name} ({type}) — сальдо на {upto}: {bal}",
    "tool.log.documents": "{n} документов",
    "tool.meta": "Мета",
    "tool.log.not_found": "не найден",
    "tool.doc_not_found": "документ {doc_id} не найден",
    "tool.pnl": "Период {start}—{end}: доходы {income} | расходы {expense} | результат {net}",
    "tool.posted": "проведено {eid}",
    "tool.log.error": "ОШИБКА: {ex}",
    "tool.error": "ошибка: {ex}",
    "spec.chart_of_accounts.params": "",
    "spec.chart_of_accounts.desc": "полный план счетов, включая счета с нулевым сальдо",
    "spec.trial_balance.params": "upto?: YYYY-MM-DD",
    "spec.trial_balance.desc": "оборотно-сальдовая ведомость (нулевые сальдо скрыты)",
    "spec.journal.params": "start?, end?, account?",
    "spec.journal.desc": "проводки периода, опц. по счёту",
    "spec.account_detail.params": "code, upto?",
    "spec.account_detail.desc": "сальдо счёта",
    "spec.list_documents.params": "kind?: vendor_invoice|bank_statement|contract|email|policy",
    "spec.list_documents.desc": "список документов",
    "spec.read_document.params": "doc_id",
    "spec.read_document.desc": "прочитать документ",
    "spec.pnl.params": "start?, end?",
    "spec.pnl.desc": "отчёт о прибылях и убытках",
    "spec.post_entry.params": "date, memo, lines[{{account,debit,credit}}]",
    "spec.post_entry.desc": "провести корректировку",

    # --- cli ---
    "cli.tool_line": "- {name}({params}) — {desc}",
    "cli.started": "Эпизод начат. Период: {start} — {end}. Компания: {name}.",
    "cli.counts": "Проводок в книге: {entries}. Документов: {documents}.",
    "cli.task": "\nЗАДАЧА: найди и исправь ВСЕ ошибки закрытия. Корректировки проводи датой {end}.",
    "cli.no_extra": "Не проводи лишнего: каждая проводка должна исправлять конкретную найденную ошибку.",
    "cli.tools": "\nИнструменты:\n{tools}",
    "cli.session_not_found": "сессия не найдена",
    "cli.closed": "эпизод завершён: после оценки изменения запрещены",
    "cli.bad_json": "неверный JSON: {e}",
    "cli.no_tool": "нет инструмента {tool}",
    "cli.bad_params": "неверные параметры: {e}",

    # --- runner ---
    "runner.system": (
        "Ты — бухгалтер, закрывающий период. Тебе доступна учётная система компании через инструменты.\n"
        "\n"
        "ЗАДАЧА: закрыть период {start} — {end}. Найди и исправь ВСЕ ошибки: непроведённые документы,\n"
        "дубли, неверную классификацию, ошибки отсечения периода (cut-off), несверенный банк.\n"
        "Корректировки проводи датой конца периода. Не проводи лишнего: каждая проводка должна\n"
        "исправлять конкретную найденную ошибку.\n"
        "\n"
        "ИНСТРУМЕНТЫ — вызывай строго по одному в строке в формате:\n"
        "CALL имя {{\"параметр\": \"значение\"}}\n"
        "\n"
        "Доступно:\n"
        "{tools}\n"
        "\n"
        "Когда закончишь — напиши ГОТОВО и краткий список исправленного.\n"
        "Работай последовательно: сначала изучи оборотку, журнал и документы, потом проводи корректировки."),
    "runner.begin": "Начинай закрытие периода.",
    "runner.turn": "--- ход {n} ---",
    "runner.done": "ГОТОВО",
    "runner.no_tool": "нет такого инструмента: {name}",
    "runner.bad_params": "неверные параметры {name}: {e}",
    "runner.bad_json": "[{name}] неверный JSON параметров",
    "runner.results": "Результаты:\n{obs}",
    "runner.summary": "ИТОГ:",

    # --- pack ---
    "pack.total": "... всего задач: {n}",
}

EN = {
    "company": "Ridge Ltd",

    # --- chart of accounts ---
    "coa.1000": "Cash at bank",
    "coa.1100": "Accounts receivable",
    "coa.1200": "Inventory",
    "coa.1300": "Prepaid expenses",
    "coa.1500": "Fixed assets",
    "coa.1590": "Accumulated depreciation",
    "coa.2000": "Accounts payable",
    "coa.2100": "Accrued liabilities",
    "coa.2200": "Payroll payable",
    "coa.2300": "VAT payable",
    "coa.2400": "Deferred revenue",
    "coa.2500": "Intercompany balances",
    "coa.3000": "Share capital",
    "coa.3100": "Retained earnings",
    "coa.4000": "Revenue",
    "coa.5000": "Cost of sales",
    "coa.6000": "Salaries and wages",
    "coa.6100": "Rent",
    "coa.6200": "Electricity and utilities",
    "coa.6300": "Professional services",
    "coa.6400": "Depreciation",
    "coa.6500": "Software",
    "coa.6600": "Telecom and security",
    "coa.6700": "Foreign exchange differences",
    "coa.6800": "Insurance",
    "coa.6900": "Other expenses",

    # --- opening entries ---
    "je.founder": "Founder's capital contribution",
    "je.opening_stock": "Opening inventory purchase",
    "je.equipment": "Equipment purchase",
    "je.insurance_policy": "Annual insurance policy",

    # --- regular month ---
    "je.revenue": "Revenue for {mon} {y}",
    "je.goods_received": "Goods received {mon} {y}",
    "je.cogs": "Cost of sales for {mon} {y}",
    "je.customer_receipts": "Customer receipts {mon}",
    "je.supplier_payment": "Payment to goods suppliers {mon}",
    "je.rent": "Rent {mon} {y}",
    "je.payroll": "Payroll {mon} {y}",
    "je.payroll_accrual": "Payroll accrual {mon} {y}",
    "je.electricity": "Electricity {mon} {y}",
    "je.telecom": "Telecom and security {mon} {y}",
    "je.insurance_amort": "Insurance amortisation {mon} {y}",
    "je.depreciation": "Depreciation {mon} {y}",
    "doc.util.title": "Electricity invoice, {mon} {y}, Gridpower Utilities",
    "doc.util.body": "Period: {mon} {y}\nTariff: commercial C2\nConsumption: {kwh} kWh\nAmount due: {util}.00",
    "vendor.util": "Gridpower Utilities",

    # --- E1 unrecorded_invoice ---
    "doc.sub.title": "Contractor invoice, Torium Ltd",
    "doc.sub.body": "Certificate of completed work for {mon} {y}\nSubcontracting services\nAmount due: {amt}.00\nCertificate date: {date}",
    "doc.sub.body_decoy": "Certificate of completed work for {mon} {y}\nSubcontracting services\nAmount due: {amt}.00",
    "vendor.torium": "Torium Ltd",
    "je.sub_decoy": "Torium, subcontracting certificate",
    "err.unrecorded_invoice": "Contractor invoice SUB for {amt} not recorded: cost of sales and payables understated",

    # --- E2 duplicate_invoice ---
    "memo.aud.plain": "Professional services, audit (invoice AUD-114)",
    "memo.aud.terse": "Audit-Pro, inv. AUD-114",
    "memo.aud.terse2": "Audit-Pro, Q3 certificate",
    "doc.aud.title": "Invoice from Audit-Pro Ltd, AUD-114",
    "doc.aud.body": "Audit services for Q3\nAmount due: {amt}.00\nInvoice number: AUD-114",
    "vendor.audit": "Audit-Pro Ltd",
    "err.duplicate_invoice": "Invoice AUD-114 posted twice ({e1} and {e2}): expenses and payables overstated by {amt}",

    # --- E3 capex_expensed ---
    "memo.hw.plain": "Server equipment purchase",
    "memo.hw.terse": "Payment of inv. HW-7781, Technostock",
    "doc.hw.title": "Invoice from Technostock Ltd, HW-7781",
    "doc.hw.body": "Server equipment, useful life 5 years\nCost: {amt}.00\nFixed asset, inventory no. FA-114\nCommissioning date: {y}-12-01",
    "doc.hw.body_decoy": "Server equipment, useful life 5 years\nCost: {amt}.00\nFixed asset, inventory no. FA-114\nCommissioning date: {y}-12-01 (not in use during the reporting period)",
    "vendor.hw": "Technostock Ltd",
    "err.capex_expensed": "Equipment costing {amt} with a 5-year useful life charged to other expenses instead of fixed assets",

    # --- E4 prepaid_not_deferred ---
    "memo.sw.plain": "Software licence, 12 months",
    "memo.sw.terse": "Softline, inv. SW-900",
    "doc.sw.title": "Software licence agreement SW-900",
    "doc.sw.body": "Term: 12 months from {date}\nCost: {amt}.00\nPaid upfront for the full term",
    "doc.sw.body_decoy": "Term: 1 month ({mon} {y})\nCost: {amt}.00\nBilled monthly in arrears.",
    "vendor.sw": "Softline Ltd",
    "err.prepaid_not_deferred": "Annual licence {amt} expensed in full; only {monthly} belongs to the period",

    # --- E5 revenue_cutoff ---
    "memo.adv.plain": "Advance from customer Vector",
    "memo.adv.terse": "Receipt from Vector, contract ADV-51",
    "doc.adv.title": "Contract with Vector Ltd, ADV-51",
    "doc.adv.body": "Prepayment: {amt}.00\nService period: January–March {y1}\nNo services were rendered in the reporting period",
    "doc.adv.body_decoy": "Payment: {amt}.00 for services rendered in {mon} {y}\nCertificate signed {date}; revenue recognised earlier.",
    "customer.vector": "Vector Ltd",
    "err.revenue_cutoff": "Advance {amt} for next year's services recognised as revenue of the period",

    # --- E6 unrecorded_bank_fee ---
    "err.unrecorded_bank_fee": "Bank fee {amt} appears on the statement but is not recorded",

    # --- E7 misclassified_expense ---
    "memo.ar.plain": "Payment under warehouse lease (AR-77)",
    "memo.ar.terse": "Storeservice, contract AR-77",
    "doc.ar.title": "Warehouse lease agreement AR-77",
    "doc.ar.body": "Subject: lease of a 400 sq m warehouse\nRent for {mon} {y}: {amt}.00\nType: operating lease of premises",
    "doc.ar.body_decoy": "Subject: lease of a 400 sq m warehouse\nRent for {mon} {y}: {amt}.00",
    "vendor.ar": "Storeservice Ltd",
    "err.misclassified_expense": "Warehouse rent {amt} charged to professional services (6300) instead of rent (6100)",

    # --- E8 intercompany_mismatch ---
    "doc.ic.title": "Email from subsidiary: intercompany reconciliation",
    "doc.ic.body": "Colleagues, per our records we rendered services to you for {amt}.00 in {mon} {y} (certificate {ic}). The amount is missing from your trial balance — please record it on the intercompany account before close.",
    "doc.ic.body_decoy": "Colleagues, we have reconciled the balances for {mon} {y}: no discrepancies, no mutual obligations outstanding at period end.",
    "counterparty.subsidiary": "subsidiary",
    "err.intercompany_mismatch": "Intercompany services {amt} not recorded: consolidation mismatch",

    # --- E9, E13–E17: absence errors ---
    "err.missing_recurring": "Telecom and security accrual {amt} missing for {mon} {y}; present in every other month of the year",
    "err.depreciation_stopped": "Depreciation 4000 not charged for {mon} {y}; the DEP series is broken",
    "err.prepaid_amort_stopped": "Annual insurance amortisation {amt} not posted for {mon} {y}; prepaid balance overstated",
    "err.accrual_not_released": "On the {mon} {y} payroll run the prior month's accrual {amt} was not released: the full amount went to expense, liability 2200 left hanging",
    "err.inventory_receipt_gap": "Goods receipt for {mon} {y} of {amt} not recorded although cost of sales was booked: inventory and payables understated",
    "err.payroll_cutoff": "Payroll accrual for {tail} days ({amt}) not booked for {mon} {y}; booked in every other month",

    # --- E10 fx_revaluation ---
    "memo.nw.plain": "Import delivery, invoice in euro",
    "memo.nw.terse": "Nordwerk GmbH, inv. NW-2210",
    "je.nw_settle": "Settlement of NW-2210",
    "doc.nw.title": "Invoice from Nordwerk GmbH, NW-2210",
    "doc.nw.body": "Delivery of components\nAmount: EUR {eur}.00\nPayment terms: 60 days\nOn the delivery date ({date}) the liability was translated at rate {r1}.\nThe payable remains outstanding at period end.",
    "doc.nw.body_decoy": "Delivery of components\nAmount: EUR {eur}.00\nThe liability was translated at rate {r1} and settled on {date} at the same rate.",
    "vendor.nw": "Nordwerk GmbH",
    "doc.fx.title": "Exchange rate notice",
    "doc.fx.body": "EUR rate on {date}: {r1}\nEUR rate on {end}: {r2}\nOutstanding foreign-currency liabilities are revalued at the reporting date.",
    "doc.fx.body_decoy": "EUR rate on {date}: {r1}\nEUR rate on {end}: {r1}\nNo foreign-currency liabilities outstanding at the reporting date.",
    "err.fx_revaluation": "Foreign-currency payable EUR {eur} not revalued: rate rose from {r1} to {r2}, difference {diff}",

    # --- E11 depreciation_prorata ---
    "memo.ml.plain": "Packaging line purchase",
    "memo.ml.terse": "Payment of inv. ML-330, Mechline",
    "je.ml_dep_decoy": "Depreciation of FA-221 for {days} days",
    "doc.ml.title": "Invoice from Mechline Ltd, ML-330",
    "doc.ml.body": "Packaging line, inventory no. FA-221\nCost: {amt}.00\nUseful life: 5 years\nCommissioned: {date} (acceptance certificate signed)",
    "vendor.ml": "Mechline Ltd",
    "err.depreciation_prorata": "Fixed asset {amt} commissioned {date}; depreciation for {days} days ({dep}) not charged",

    # --- E12 service_span_cutoff ---
    "memo.qb.plain": "Project support, 60 days",
    "memo.qb.terse": "Qubit, contract QB-88",
    "doc.qb.title": "Support agreement QB-88 (Qubit Ltd)",
    "doc.qb.body": "Service period: {start} to {end} (60 calendar days)\nCost: {amt}.00, paid upfront in a single instalment\nServices are rendered evenly over the contract term.",
    "doc.qb.body_decoy": "Service period: {start} to {end} (within the reporting period)\nCost: {amt}.00\nWork accepted in full; certificate signed {end}.",
    "vendor.qb": "Qubit Ltd",
    "err.service_span_cutoff": "Contract QB-88 for {amt} over 60 days expensed in full; {in_period} days fall in the period, {defer} to be deferred",

    # --- legitimate distractors ---
    "je.cs": "Cleanservice, inv. {n}",
    "doc.cs.title": "Invoice from Cleanservice Ltd, {n}",
    "doc.cs.body": "Office cleaning, {per} of {mon} {y}\nAmount due: {amt}.00\nThe contract provides for two certificates per month.",
    "half.first": "first half",
    "half.second": "second half",
    "vendor.cs": "Cleanservice Ltd",
    "je.pt": "Promtech, inv. PT-55",
    "doc.pt.title": "Invoice from Promtech Ltd, PT-55",
    "doc.pt.body": "Consumables and components (useful life under 12 months)\nAmount due: {amt}.00\nNot a fixed asset: unit cost below the capitalisation threshold.",
    "vendor.pt": "Promtech Ltd",

    # --- accounting policy and bank statement ---
    "doc.pol.title": "Accounting policy (extract)",
    "doc.pol.body": (
        "1. Depreciation is charged on a straight-line basis from the day the asset is "
        "commissioned, inclusive, pro rata to the number of days in the month.\n"
        "2. Salaries are paid on the 25th for the 1st to the 25th; "
        "the remaining days of the month (in {mon} {y} — {tail} days) "
        "are accrued at month end and released with the next payroll run.\n"
        "3. Expenses under contracts that span the period end "
        "are allocated evenly by calendar day.\n"
        "4. Outstanding foreign-currency liabilities are revalued "
        "at the reporting-date rate; the difference is charged to foreign exchange differences.\n"
        "5. Fixed-asset capitalisation threshold: 50,000. Below the threshold — expense of the period.\n"
        "6. Prepaid expenses (insurance policy) are amortised in equal "
        "monthly instalments over the policy term.\n"
        "7. The payroll accrual is released with the next payroll run.\n"
        "8. Closing adjustments are posted on the last day of the period, including "
        "corrections of omissions in prior months of the current year."),
    "doc.bank.title": "Bank statement for {mon} {y}",
    "doc.bank.body_nofee": "Closing balance per statement: {bal}\nAll movements of the period are recorded in the ledger; no discrepancies.",
    "doc.bank.body_fee": "Closing balance per statement: {bal}\nIncludes a debit: account maintenance fee {fee}.00 ({date})",

    # --- ledger ---
    "ledger.no_lines": "entry has no lines",
    "ledger.unknown_account": "unknown account {account}",
    "ledger.negative": "negative amounts are not allowed",
    "ledger.both_sides": "a line cannot be both debit and credit",
    "ledger.unbalanced": "out of balance: Dr {d} ≠ Cr {c}",

    # --- tools ---
    "tool.coa_header": "code | " + "name".ljust(35) + " | type",
    "tool.log.accounts": "{n} accounts",
    "tool.tb_header": "code | " + "account".ljust(33) + " | " + "debit".rjust(10) + " | " + "credit".rjust(10),
    "tool.tb_total": "TOTAL: Dr {d} | Cr {c} | {status}",
    "tool.balanced": "balanced",
    "tool.unbalanced": "OUT OF BALANCE",
    "tool.log.rows": "{n} rows",
    "tool.dr": "Dr",
    "tool.cr": "Cr",
    "tool.log.entries": "{n} entries",
    "tool.empty": "(empty)",
    "tool.log.no_account": "no such account",
    "tool.no_account": "account {code} is not in the chart of accounts. See the full list: chart_of_accounts",
    "tool.balance": "{code} {name} ({type}) — balance as of {upto}: {bal}",
    "tool.log.documents": "{n} documents",
    "tool.meta": "Meta",
    "tool.log.not_found": "not found",
    "tool.doc_not_found": "document {doc_id} not found",
    "tool.pnl": "Period {start}—{end}: income {income} | expenses {expense} | net {net}",
    "tool.posted": "posted {eid}",
    "tool.log.error": "ERROR: {ex}",
    "tool.error": "error: {ex}",
    "spec.chart_of_accounts.params": "",
    "spec.chart_of_accounts.desc": "full chart of accounts, including zero-balance accounts",
    "spec.trial_balance.params": "upto?: YYYY-MM-DD",
    "spec.trial_balance.desc": "trial balance (zero balances hidden)",
    "spec.journal.params": "start?, end?, account?",
    "spec.journal.desc": "entries of the period, optionally filtered by account",
    "spec.account_detail.params": "code, upto?",
    "spec.account_detail.desc": "account balance",
    "spec.list_documents.params": "kind?: vendor_invoice|bank_statement|contract|email|policy",
    "spec.list_documents.desc": "list documents",
    "spec.read_document.params": "doc_id",
    "spec.read_document.desc": "read a document",
    "spec.pnl.params": "start?, end?",
    "spec.pnl.desc": "profit and loss statement",
    "spec.post_entry.params": "date, memo, lines[{{account,debit,credit}}]",
    "spec.post_entry.desc": "post an adjusting entry",

    # --- cli ---
    "cli.tool_line": "- {name}({params}) — {desc}",
    "cli.started": "Episode started. Period: {start} — {end}. Company: {name}.",
    "cli.counts": "Entries in the ledger: {entries}. Documents: {documents}.",
    "cli.task": "\nTASK: find and fix ALL closing errors. Post adjustments dated {end}.",
    "cli.no_extra": "Do not post anything unnecessary: every entry must fix a specific error you found.",
    "cli.tools": "\nTools:\n{tools}",
    "cli.session_not_found": "session not found",
    "cli.closed": "episode is closed: no changes allowed after grading",
    "cli.bad_json": "invalid JSON: {e}",
    "cli.no_tool": "no such tool: {tool}",
    "cli.bad_params": "invalid parameters: {e}",

    # --- runner ---
    "runner.system": (
        "You are an accountant closing the period. You have access to the company's accounting system through tools.\n"
        "\n"
        "TASK: close the period {start} — {end}. Find and fix ALL errors: unrecorded documents,\n"
        "duplicates, misclassifications, period cut-off errors, unreconciled bank items.\n"
        "Post adjustments dated the last day of the period. Do not post anything unnecessary: every entry must\n"
        "fix a specific error you found.\n"
        "\n"
        "TOOLS — call strictly one per line, in the format:\n"
        "CALL name {{\"param\": \"value\"}}\n"
        "\n"
        "Available:\n"
        "{tools}\n"
        "\n"
        "When you are finished, write DONE and a short list of what you fixed.\n"
        "Work sequentially: first study the trial balance, the journal and the documents, then post adjustments."),
    "runner.begin": "Begin the period close.",
    "runner.turn": "--- turn {n} ---",
    "runner.done": "DONE",
    "runner.no_tool": "no such tool: {name}",
    "runner.bad_params": "invalid parameters for {name}: {e}",
    "runner.bad_json": "[{name}] invalid JSON in parameters",
    "runner.results": "Results:\n{obs}",
    "runner.summary": "SUMMARY:",

    # --- pack ---
    "pack.total": "... total tasks: {n}",
}

TABLES = {"ru": RU, "en": EN}

_missing = set(RU) ^ set(EN)
if _missing:
    raise RuntimeError(f"closebench.strings: RU/EN key sets differ: {sorted(_missing)}")

def T(lang: str, key: str, **fmt) -> str:
    """Строка `key` на языке `lang`, отформатированная `fmt`. Не трогает rng."""
    try:
        table = TABLES[lang]
    except KeyError:
        raise ValueError(f"unsupported lang {lang!r}; expected one of {LANGS}") from None
    return table[key].format(**fmt)
