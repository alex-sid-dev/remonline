<template>
  <div class="info-page">
    <h2 class="form-title info-page-title">Справка по системе RemOnline</h2>

    <section class="info-section">
      <h3 class="info-section-title">Роли и права доступа</h3>
      <ul class="info-list">
        <li><strong>Супервайзер</strong> — полный доступ: заказы, сотрудники, запчасти, бренды, типы устройств, статистика; создание и редактирование супервизоров; ввод реквизитов организации; смена паролей и зарплатные настройки.</li>
        <li><strong>Админ</strong> — управление заказами, сотрудниками (кроме супервизора), запчастями, брендами, типами устройств, статистика. Не может редактировать карточку супервизора и вводить данные организации.</li>
        <li><strong>Менеджер</strong> — создание и редактирование заказов, управление брендами и типами устройств, просмотр заказов и статистики. Не управляет сотрудниками и запчастями.</li>
        <li><strong>Мастер</strong> — выполнение работ по заказам, добавление работ и запчастей к заказу, управление брендами и типами устройств. Ограниченный доступ к смене статусов заказа.</li>
      </ul>
    </section>

    <section class="info-section">
      <h3 class="info-section-title">Создание заказа</h3>
      <p>Новый заказ создаётся одним запросом (клиент + устройство + заказ):</p>
      <ul class="info-list">
        <li>Укажите <strong>телефон</strong> — при совпадении подтянутся существующие клиенты.</li>
        <li>Заполните <strong>ФИО</strong>, при необходимости адрес, email, Telegram.</li>
        <li>Укажите <strong>устройство</strong>: тип, бренд, модель, серийный номер (по серийному номеру ищется существующее устройство).</li>
        <li>Выберите <strong>менеджера</strong> (принявшего заказ), опишите <strong>неисправность</strong>.</li>
      </ul>
      <p>Если клиент или устройство с такими данными уже есть — они будут привязаны; иначе создаются новые. Цена заказа считается на бэкенде по работам и запчастям.</p>
    </section>

    <section class="info-section">
      <h3 class="info-section-title">Редактирование заказа</h3>
      <ul class="info-list">
        <li>Клиент, устройство, неисправность, менеджер, инженер можно менять в карточке заказа.</li>
        <li><strong>Статус заказа</strong> зависит от роли: супервайзер видит все переходы, менеджер — ограниченный набор (например, без перевода в «Закрыт»).</li>
        <li>Работы и запчасти добавляются в карточке заказа; итоговая сумма пересчитывается на сервере.</li>
        <li>Доступны печать <strong>акта выполненных работ</strong> и <strong>квитанции о сдаче техники</strong> (в них подставляются реквизиты организации, если они введены супервизором).</li>
      </ul>
    </section>

    <section class="info-section">
      <h3 class="info-section-title">Ограничения</h3>
      <ul class="info-list">
        <li>Удалить можно только заказы в допустимых статусах (на бэкенде).</li>
        <li>Супервизора нельзя удалить; карточку супервизора может редактировать только супервизор.</li>
        <li>Реквизиты организации (для квитанций и актов) задаёт только супервизор, в окне редактирования сотрудника — кнопка «Ввести данные организации» в шапке.</li>
        <li>Валидация паролей и полей (email, телефон и т.д.) выполняется по правилам с бэкенда (раздел «Правила валидации»).</li>
      </ul>
    </section>

    <section class="info-section">
      <h3 class="info-section-title">Бренды и типы устройств</h3>
      <p>В боковом меню доступны разделы <strong>Бренды</strong> и <strong>Типы устройств</strong>. Они нужны для единообразного указания устройства при создании заказа.</p>
      <ul class="info-list">
        <li><strong>Бренды</strong> — производители техники (Samsung, Apple, Xiaomi и т.д.). При создании заказа бренд выбирается из списка. Создание, редактирование и удаление доступны супервайзеру, админу, мастеру и менеджеру. Удалить бренд нельзя, если на него ссылается хотя бы одно устройство.</li>
        <li><strong>Типы устройств</strong> — категории техники (смартфон, ноутбук, планшет и т.д.). У каждого типа можно указать название и описание. Управление (создание, редактирование, удаление) доступно тем же ролям. Тип нельзя удалить, если он привязан к устройствам.</li>
      </ul>
    </section>

    <section class="info-section">
      <h3 class="info-section-title">Сотрудники и организация</h3>
      <ul class="info-list">
        <li>Создавать и редактировать сотрудников могут супервайзер и админ. Создать роль «супервизор» может только супервизор.</li>
        <li>Смена пароля сотрудника — супервайзер (любой сотрудник) или админ (только мастер/менеджер).</li>
        <li>Реквизиты организации (название, ИНН, адрес, КПП, р/с, к/с, БИК) вводятся супервизором и используются в печатных формах.</li>
      </ul>
    </section>

    <footer class="info-footer">
      <span class="info-footer-label">Сделано</span>
      <span class="info-footer-name">Сидоренко Александр</span>
      <span class="info-footer-sep">·</span>
      <a class="info-footer-link" href="https://t.me/Azzlem" target="_blank" rel="noopener noreferrer">tg: @Azzlem</a>
      <span class="info-footer-sep">·</span>
      <a class="info-footer-link" href="mailto:azzlem@mail.ru">azzlem@mail.ru</a>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.info-page {
  padding: 20px 24px;
  max-width: 720px;
}
.info-page-title {
  margin-bottom: 24px;
  font-size: 1.5rem;
}
.info-section {
  margin-bottom: 28px;
}
.info-section-title {
  font-size: 1.1rem;
  margin: 0 0 10px;
  color: #e5e7eb;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
  padding-bottom: 6px;
}
.info-list {
  margin: 0;
  padding-left: 20px;
  line-height: 1.6;
  color: #cbd5e1;
}
.info-list li {
  margin-bottom: 8px;
}
.info-section p {
  margin: 0 0 10px;
  line-height: 1.6;
  color: #cbd5e1;
}

.info-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  font-size: 0.9rem;
  color: #94a3b8;
}
.info-footer-label {
  color: #64748b;
}
.info-footer-name {
  color: #e2e8f0;
  font-weight: 500;
}
.info-footer-sep {
  color: #475569;
  user-select: none;
}
.info-footer-link {
  color: #38bdf8;
  text-decoration: none;
}
.info-footer-link:hover {
  text-decoration: underline;
}
</style>
