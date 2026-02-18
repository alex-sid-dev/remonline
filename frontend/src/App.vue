<template>
  <div class="shell">
    <header class="shell-header">
      <div class="brand">
        <div class="brand-mark" />
        <div>
          <div class="brand-title">RemOnline</div>
          <div class="brand-subtitle">
            панель управления сервисом
          </div>
        </div>
      </div>

      <div class="user-controls">
        <template v-if="isAuthenticated">
          <span>{{ lastLoginEmail || 'Пользователь' }}</span>
          <button
            class="btn btn-ghost"
            type="button"
            @click="handleLogout"
          >
            Выйти
          </button>
        </template>
        <template v-else>
          <button
            class="btn btn-primary"
            type="button"
            @click="openLoginModal"
          >
            Войти
          </button>
        </template>
      </div>
    </header>

    <section class="shell-body">
      <aside class="side-panel">
        <h2 class="side-title">
          Разделы
        </h2>

        <p class="side-description">
          Выберите, с чем работать сейчас.
        </p>

        <div class="divider" />

        <nav class="side-nav">
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'orders' }"
            type="button"
            @click="() => changeTab('orders')"
          >
            Заказы
          </button>
          <button
            v-if="userRole === 'supervisor' || userRole === 'admin'"
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'employees' }"
            type="button"
            @click="() => changeTab('employees')"
          >
            Сотрудники
          </button>
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'parts' }"
            type="button"
            @click="() => changeTab('parts')"
          >
            Запчасти
          </button>
        </nav>
      </aside>

      <main class="main-panel">
        <section class="table-shell">
          <!-- Обычный заголовок списка -->
          <header
            v-if="!(activeTab === 'orders' && orderDetails.data)"
            class="table-header"
          >
            <div class="table-title">
              <span v-if="activeTab === 'orders'">Заказы</span>
              <span v-else-if="activeTab === 'employees'">Сотрудники</span>
              <span v-else>Запчасти</span>
            </div>
            <div class="table-meta">
              <span v-if="!isAuthenticated">
                Чтобы работать с API, авторизуйтесь.
              </span>
              <span v-else-if="isLoading">
                Загрузка данных…
              </span>
              <span v-else-if="loadError">
                Ошибка: {{ loadError }}
              </span>
              <span v-else>
                {{ currentCount }} записей
              </span>
            </div>
          </header>
          <!-- Заголовок страницы заказа: только «Назад» и крупный номер по центру -->
          <header
            v-else
            class="order-detail-header"
          >
            <button
              class="btn btn-ghost"
              type="button"
              @click="() => { orderDetails.data = null; }"
            >
              ← Назад к списку
            </button>
            <h1 class="order-detail-title">
              Заказ #{{ orderDetails.data.id }}
            </h1>
            <div />
          </header>

          <div class="table-wrapper">
            <div v-if="!isAuthenticated" class="empty-state">
              Войдите, чтобы получить доступ к REST API.
            </div>

            <div
              v-else-if="isLoading"
              class="empty-state"
            >
              <span class="loader">
                <span class="loader-dot" />
                <span class="loader-dot" />
                <span class="loader-dot" />
              </span>
            </div>

            <div
              v-else-if="loadError"
              class="empty-state"
            >
              {{ loadError }}
            </div>

            <template v-else>
              <!-- Заказы -->
              <div v-if="activeTab === 'orders' && !orderDetails.data">
                <!-- Экран создания нового заказа (отдельно от списка) -->
                <div
                  v-if="orderForm.open && !orderForm.editMode"
                  class="login-card"
                  style="margin-top: 12px;"
                >
                  <div class="field">
                    <div class="field-label">
                      Новый заказ
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-client">Клиент</label>
                    <div class="field-row">
                      <input
                        v-model="orderClientSearch"
                        class="field-input"
                        type="text"
                        placeholder="Поиск по ФИО или телефону (от 3 символов)"
                        @input="handleOrderClientSearchInput"
                        @focus="handleOrderClientSearchInput"
                      >
                      <button
                        class="btn btn-ghost"
                        type="button"
                        @click="startCreateClientForOrder"
                      >
                        + Новый
                      </button>
                    </div>
                    <div
                      v-if="orderClientSuggestionsOpen && orderClientSearch.length >= 3"
                      class="autocomplete-list"
                    >
                      <button
                        v-for="c in clientsForOrder"
                        :key="c.uuid"
                        type="button"
                        class="autocomplete-item"
                        @click="selectOrderClient(c)"
                      >
                        <div class="autocomplete-item-main">
                          {{ c.full_name }}
                        </div>
                        <div class="autocomplete-item-sub">
                          {{ c.phone || '—' }}
                        </div>
                      </button>
                      <div
                        v-if="!clientsForOrder.length"
                        class="autocomplete-empty"
                      >
                        Ничего не найдено
                      </div>
                    </div>
                    <div class="hint">
                      Клиент подставится автоматически. Если клиента нет в списке — создайте его через «+ Новый».
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-device">Устройство</label>
                    <div class="field-row">
                      <button
                        class="btn btn-ghost"
                        type="button"
                        @click="startCreateDeviceForOrder"
                      >
                        + Новое
                      </button>
                    </div>
                    <div class="hint">
                      Для нового заказа всегда создаётся новое устройство. Нажмите «+ Новое», чтобы заполнить данные устройства для выбранного клиента.
                    </div>
                  </div>
                  <div
                    v-if="userRole === 'supervisor' || userRole === 'admin'"
                    class="field"
                  >
                    <label class="field-label" for="order-engineer">Инженер</label>
                    <select
                      id="order-engineer"
                      v-model="orderForm.data.assigned_employee_uuid"
                      class="field-input"
                    >
                      <option value="">Не назначен</option>
                      <option
                        v-for="e in employees"
                        :key="e.uuid"
                        :value="e.uuid"
                      >
                        {{ e.full_name }} ({{ e.position }})
                      </option>
                    </select>
                  </div>
                  <div
                    v-if="userRole === 'supervisor' || userRole === 'admin'"
                    class="field"
                  >
                    <label class="field-label" for="order-manager">Менеджер</label>
                    <select
                      id="order-manager"
                      v-model="orderForm.data.manager_uuid"
                      class="field-input"
                    >
                      <option value="">Текущий менеджер (по умолчанию)</option>
                      <option
                        v-for="e in employees.filter((e) => e.position === 'manager')"
                        :key="e.uuid"
                        :value="e.uuid"
                      >
                        {{ e.full_name }}
                      </option>
                    </select>
                  </div>
                  <div
                    v-else
                    class="field"
                  >
                    <label class="field-label">Менеджер</label>
                    <div class="order-info-value">
                      {{ currentEmployeeName || 'Текущий пользователь' }}
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-status">Статус</label>
                    <select
                      id="order-status"
                      v-model="orderForm.data.status"
                      class="field-input"
                    >
                      <option
                        v-for="s in ORDER_STATUS_OPTIONS"
                        :key="s.value"
                        :value="s.value"
                      >
                        {{ s.label }}
                      </option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-problem">Проблема</label>
                    <input
                      id="order-problem"
                      v-model="orderForm.data.problem_description"
                      class="field-input"
                      type="text"
                    >
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-comment">Комментарий</label>
                    <input
                      id="order-comment"
                      v-model="orderForm.data.comment"
                      class="field-input"
                      type="text"
                    >
                  </div>
                  <div class="field">
                    <button
                      class="btn btn-primary"
                      type="button"
                      :disabled="!orderFormValid"
                      @click="submitOrderForm"
                    >
                      Сохранить
                    </button>
                  </div>
                </div>

                <!-- Список заказов + форма редактирования -->
                <div v-else>
                  <div class="table-header">
                  <div class="table-meta">
                    Заказы: выбор клиента и устройства из существующих сущностей, изменение статуса и цены.
                    <div class="table-status-filters">
                      <button
                        v-for="s in ORDER_STATUS_OPTIONS"
                        :key="s.value"
                        class="btn btn-ghost table-status-filter-pill"
                        :class="[
                          tableStatusFilterClass(s.value),
                          { 'table-status-filter-pill--active': orderStatusFilter.includes(s.value) },
                        ]"
                        type="button"
                        @click.stop="toggleOrderStatusFilter(s.value)"
                      >
                        {{ s.label }}
                      </button>
                      <button
                        v-if="orderStatusFilter.length"
                        class="btn btn-ghost table-status-filter-clear"
                        type="button"
                        @click.stop="clearOrderStatusFilter"
                      >
                        Сбросить
                      </button>
                    </div>
                  </div>
                  <button
                    v-if="userRole === 'supervisor' || userRole === 'admin' || userRole === 'manager'"
                    class="btn btn-primary"
                    type="button"
                    @click="startCreateOrder"
                  >
                    Новый заказ
                  </button>
                </div>
                <table v-if="orders.length">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Клиент</th>
                      <th>Устройство</th>
                      <th>Менеджер</th>
                      <th>Инженер</th>
                      <th>Статус</th>
                      <th>Цена</th>
                      <th>Создано</th>
                      <th>Обновлено</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="order in filteredOrders"
                      :key="order.uuid"
                      @click="openOrderDetails(order)"
                    >
                      <td>{{ order.id }}</td>
                      <td>{{ clientLabel(order.client_id) }}</td>
                      <td>{{ deviceLabel(order.device_id) }}</td>
                      <td>{{ employeeLabel(order.creator_id) }}</td>
                      <td>{{ employeeLabel(order.assigned_employee_id) }}</td>
                      <td>
                        <span
                          class="badge badge--status"
                          :class="orderStatusClass(order.status)"
                        >
                          {{ orderStatusLabel(order.status) }}
                        </span>
                      </td>
                      <td>{{ order.price ?? '—' }}</td>
                      <td>{{ formatDate(order.created_at) }}</td>
                      <td>{{ formatDate(order.updated_at) }}</td>
                      <td>
                        <button
                          class="btn btn-ghost"
                          type="button"
                          @click="startEditOrder(order)"
                        >
                          Изменить
                        </button>
                        <button
                          class="btn btn-ghost"
                          type="button"
                          @click="removeOrder(order)"
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-state">
                  Заказов пока нет.
                </div>

                <div
                  v-if="orderForm.open && orderForm.editMode"
                  class="login-card"
                  style="margin-top: 12px;"
                >
                  <div class="field">
                    <div class="field-label">
                      {{ orderForm.editMode ? 'Редактирование заказа' : 'Новый заказ' }}
                    </div>
                  </div>
                  <!-- Для редактирования клиента/устройства сейчас не меняем -->
                  <div
                    v-if="userRole === 'supervisor' || userRole === 'admin'"
                    class="field"
                  >
                    <label class="field-label" for="order-engineer">Инженер</label>
                    <select
                      id="order-engineer"
                      v-model="orderForm.data.assigned_employee_uuid"
                      class="field-input"
                    >
                      <option value="">Не назначен</option>
                      <option
                        v-for="e in employees"
                        :key="e.uuid"
                        :value="e.uuid"
                      >
                        {{ e.full_name }} ({{ e.position }})
                      </option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-status">Статус</label>
                    <select
                      id="order-status"
                      v-model="orderForm.data.status"
                      class="field-input"
                    >
                      <option
                        v-for="s in ORDER_STATUS_OPTIONS"
                        :key="s.value"
                        :value="s.value"
                      >
                        {{ s.label }}
                      </option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-price">Цена</label>
                    <input
                      id="order-price"
                      v-model.number="orderForm.data.price"
                      class="field-input"
                      type="number"
                      step="0.01"
                    >
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-problem">Проблема</label>
                    <input
                      id="order-problem"
                      v-model="orderForm.data.problem_description"
                      class="field-input"
                      type="text"
                    >
                  </div>
                  <div class="field">
                    <label class="field-label" for="order-comment">Комментарий</label>
                    <input
                      id="order-comment"
                      v-model="orderForm.data.comment"
                      class="field-input"
                      type="text"
                    >
                  </div>
                  <div class="field">
                    <button
                      class="btn btn-primary"
                      type="button"
                      :disabled="!orderFormValid"
                      @click="submitOrderForm"
                    >
                      Сохранить
                    </button>
                  </div>
                </div>
                </div>
              </div>
              <!-- Детальная страница заказа: 3 колонки -->
              <div v-else-if="activeTab === 'orders' && orderDetails.data" class="order-detail-page">
                <div v-if="orderDetails.loading" class="empty-state">
                  Загрузка деталей заказа…
                </div>

                <div v-else class="order-detail-columns">
                  <!-- Колонка 1: клиент и устройство -->
                  <aside class="order-detail-col order-detail-col--left">
                    <div class="order-info-card">
                      <div class="order-info-row">
                        <span class="order-info-label">ФИО клиента</span>
                        <span class="order-info-value">{{ orderDetails.data.client.full_name }}</span>
                      </div>
                      <div class="order-info-row">
                        <span class="order-info-label">Телефон</span>
                        <span class="order-info-value">{{ orderDetails.data.client.phone || '—' }}</span>
                      </div>
                      <div class="order-info-row">
                        <span class="order-info-label">Бренд</span>
                        <span class="order-info-value">{{ orderDetails.data.device.brand || '—' }}</span>
                      </div>
                      <div class="order-info-row">
                        <span class="order-info-label">Модель</span>
                        <span class="order-info-value">{{ orderDetails.data.device.model || '—' }}</span>
                      </div>
                      <div class="order-info-row">
                        <span class="order-info-label">Серийный номер</span>
                        <span class="order-info-value">{{ orderDetails.data.device.serial_number || '—' }}</span>
                      </div>
                      <div class="order-info-row">
                        <span class="order-info-label">Менеджер</span>
                        <span class="order-info-value">
                          {{ orderDetails.data.creator?.full_name || '—' }}
                        </span>
                      </div>
                      <div class="order-info-row">
                        <span class="order-info-label">Инженер</span>
                        <span class="order-info-value">
                          {{ orderDetails.data.assigned_employee?.full_name || '—' }}
                        </span>
                      </div>
                    </div>
                    <div class="login-card" style="margin-top: 16px;">
                      <div
                        v-if="userRole === 'supervisor' || userRole === 'admin'"
                        class="field"
                      >
                        <label class="field-label" for="details-manager">Менеджер</label>
                        <select
                          id="details-manager"
                          v-model.number="detailsManagerId"
                          class="field-input"
                        >
                          <option :value="null">Не назначен</option>
                          <option
                            v-for="e in employees.filter((e) => e.position === 'manager')"
                            :key="e.id"
                            :value="e.id"
                          >
                            {{ e.full_name }}
                          </option>
                        </select>
                      </div>
                      <div
                        v-if="userRole === 'supervisor' || userRole === 'admin'"
                        class="field"
                      >
                        <label class="field-label" for="details-engineer">Инженер</label>
                        <select
                          id="details-engineer"
                          v-model.number="detailsEngineerId"
                          class="field-input"
                        >
                          <option :value="null">Не назначен</option>
                          <option
                            v-for="e in employees.filter((e) => e.position === 'master')"
                            :key="e.id"
                            :value="e.id"
                          >
                            {{ e.full_name }}
                          </option>
                        </select>
                      </div>
                      <div class="field">
                        <label class="field-label" for="details-status">Статус</label>
                        <select
                          id="details-status"
                          v-model="orderDetails.data.status"
                          class="field-input"
                        >
                          <option
                            v-for="s in ORDER_STATUS_OPTIONS"
                            :key="s.value"
                            :value="s.value"
                          >
                            {{ s.label }}
                          </option>
                        </select>
                      </div>
                      <div class="field">
                        <label class="field-label" for="details-price">Цена (авто)</label>
                        <input
                          id="details-price"
                          :value="orderCalculatedPrice"
                          class="field-input"
                          type="number"
                          step="0.01"
                          disabled
                        >
                      </div>
                      <div class="field">
                        <label class="field-label" for="details-problem">Проблема</label>
                        <input
                          id="details-problem"
                          v-model="orderDetails.data.problem_description"
                          class="field-input"
                          type="text"
                        >
                      </div>
                      <button
                        class="btn btn-primary"
                        type="button"
                        @click="saveOrderDetails"
                      >
                        Сохранить изменения
                      </button>
                    </div>
                  </aside>

                  <!-- Колонка 2: работы и запчасти -->
                  <div class="order-detail-col order-detail-col--center">
                    <div class="order-detail-block">
                      <div class="order-detail-block-head">
                        <span class="order-detail-block-title">Работы</span>
                        <button
                          class="btn btn-primary"
                          type="button"
                          @click="openAddWorkModal"
                        >
                          + Добавить работу
                        </button>
                      </div>
                      <div v-if="orderDetails.data.works.length" class="order-detail-table-wrap">
                        <table>
                          <thead>
                            <tr>
                              <th>Название</th>
                              <th>Исполнитель</th>
                              <th>Кол-во</th>
                              <th>Цена (за всё)</th>
                              <th>Описание</th>
                              <th />
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="w in orderDetails.data.works"
                              :key="w.id"
                            >
                              <td>{{ w.title }}</td>
                              <td>{{ w.employee?.full_name || '—' }}</td>
                              <td>{{ w.qty || 1 }}</td>
                              <td>
                                {{
                                  (w.price || 0) * (w.qty || 1) || '—'
                                }}
                              </td>
                              <td>{{ w.description || '—' }}</td>
                              <td class="text-right">
                                <button
                                  class="btn btn-ghost"
                                  type="button"
                                  @click.stop="decrementWork(w)"
                                >
                                  −
                                </button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else class="empty-state">
                        Работ пока нет.
                      </div>
                    </div>
                    <div class="order-detail-block">
                      <div class="order-detail-block-head">
                        <span class="order-detail-block-title">Запчасти</span>
                        <button
                          class="btn btn-primary"
                          type="button"
                          @click="openAddPartToOrderModal"
                        >
                          + Добавить запчасть
                        </button>
                      </div>
                      <div v-if="orderDetails.data.parts.length" class="order-detail-table-wrap">
                        <table>
                          <thead>
                            <tr>
                              <th>Название</th>
                              <th>SKU</th>
                              <th>Кол-во</th>
                              <th>Цена (за всё)</th>
                              <th />
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="p in orderDetails.data.parts"
                              :key="p.id"
                            >
                              <td>{{ p.part_info?.name || '—' }}</td>
                              <td>{{ p.part_info?.sku || '—' }}</td>
                              <td>{{ p.qty }}</td>
                              <td>
                                {{
                                  (p.price ?? p.part_info?.price ?? 0) * (p.qty || 0) || '—'
                                }}
                              </td>
                              <td class="text-right">
                                <button
                                  class="btn btn-ghost"
                                  type="button"
                                  @click.stop="decrementOrderPart(p)"
                                >
                                  −
                                </button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else class="empty-state">
                        Запчастей пока нет.
                      </div>
                    </div>
                  </div>

                  <!-- Колонка 3: комментарии (чат) -->
                  <aside class="order-detail-col order-detail-col--right">
                    <div class="order-comments-chat">
                      <div class="order-comments-title">Комментарии</div>
                      <div class="order-comments-list" ref="commentsListRef">
                        <div
                          v-for="c in (orderDetails.data.comments || [])"
                          :key="c.id"
                          class="order-comment-bubble"
                        >
                          <div class="order-comment-text">{{ c.text }}</div>
                          <div class="order-comment-meta">
                            {{ formatCommentDate(c.created_at) }}
                            <span v-if="c.creator?.full_name"> · {{ c.creator.full_name }}</span>
                          </div>
                        </div>
                        <div v-if="!(orderDetails.data.comments || []).length" class="empty-state">
                          Нет комментариев.
                        </div>
                      </div>
                      <div class="order-comments-input-row">
                        <input
                          v-model="newCommentText"
                          class="field-input order-comments-input"
                          type="text"
                          placeholder="Написать комментарий…"
                          @keydown.enter.prevent="sendOrderComment"
                        >
                        <button
                          class="btn btn-primary"
                          type="button"
                          @click="sendOrderComment"
                        >
                          Отправить
                        </button>
                      </div>
                    </div>
                  </aside>
                </div>
              </div>

              <div v-else-if="activeTab === 'employees'">
                <div class="table-header">
                  <div class="table-meta">
                    Сотрудники
                  </div>
                  <button
                    v-if="canCreateEmployees"
                    class="btn btn-primary"
                    type="button"
                    @click="startCreateEmployee"
                  >
                    Новый сотрудник
                  </button>
                </div>
                <table v-if="employees.length">
                  <thead>
                    <tr>
                      <th>ФИО</th>
                      <th>Телефон</th>
                      <th>Должность</th>
                      <th v-if="canManageEmployees" />
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="e in employees"
                      :key="e.uuid"
                    >
                      <td>{{ e.full_name }}</td>
                      <td>{{ e.phone || '—' }}</td>
                      <td>{{ e.position }}</td>
                      <td v-if="canManageEmployees">
                        <button
                          class="btn btn-ghost"
                          type="button"
                          @click="startEditEmployee(e)"
                        >
                          Изменить
                        </button>
                        <button
                          class="btn btn-ghost"
                          type="button"
                          @click="removeEmployee(e)"
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-state">
                  Сотрудников пока нет.
                </div>

                <div
                  v-if="employeeForm.open"
                  class="login-card"
                  style="margin-top: 12px;"
                >
                  <div class="field">
                    <div class="field-label">
                      {{ employeeForm.editMode ? 'Редактирование сотрудника' : 'Новый сотрудник' }}
                    </div>
                  </div>
                  <template v-if="!employeeForm.editMode">
                    <div class="field">
                      <label class="field-label" for="emp-email">Email</label>
                      <input
                        id="emp-email"
                        v-model="employeeForm.data.email"
                        class="field-input"
                        :class="{ 'field-input--error': empEmailError }"
                        type="email"
                        autocomplete="off"
                      >
                      <div v-if="empEmailError" class="error">
                        {{ empEmailError }}
                      </div>
                    </div>
                    <div class="field">
                      <label class="field-label" for="emp-password">Пароль</label>
                      <input
                        id="emp-password"
                        v-model="employeeForm.data.password"
                        class="field-input"
                        :class="{ 'field-input--error': empPasswordError }"
                        type="password"
                        autocomplete="new-password"
                      >
                      <div v-if="empPasswordError" class="error">
                        {{ empPasswordError }}
                      </div>
                    </div>
                  </template>
                  <div class="field">
                    <label class="field-label" for="emp-fullname">ФИО</label>
                    <input
                      id="emp-fullname"
                      v-model="employeeForm.data.full_name"
                      class="field-input"
                      :class="{ 'field-input--error': empFullNameError }"
                      type="text"
                    >
                    <div v-if="empFullNameError" class="error">
                      {{ empFullNameError }}
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label" for="emp-phone">Телефон</label>
                    <input
                      id="emp-phone"
                      v-model="employeeForm.data.phone"
                      class="field-input"
                      :class="{ 'field-input--error': empPhoneError }"
                      type="text"
                      placeholder="+78008008000"
                    >
                    <div class="hint">
                      Формат: +7 и 10 цифр, например +78008008000
                    </div>
                    <div v-if="empPhoneError" class="error">
                      {{ empPhoneError }}
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label" for="emp-position">Роль</label>
                    <select
                      id="emp-position"
                      v-model="employeeForm.data.position"
                      class="field-input"
                    >
                      <option value="master">
                        master
                      </option>
                      <option value="manager">
                        manager
                      </option>
                      <option value="admin">
                        admin
                      </option>
                      <option
                        v-if="userRole === 'supervisor'"
                        value="supervisor"
                      >
                        supervisor
                      </option>
                    </select>
                  </div>
                  <div class="field">
                    <button
                      class="btn btn-primary"
                      type="button"
                      :disabled="!employeeFormValid"
                      @click="submitEmployeeForm"
                    >
                      Сохранить
                    </button>
                  </div>
                </div>
              </div>
              <div v-else>
                <div class="table-header">
                  <div class="table-meta">
                    Запчасти: общий список номенклатуры.
                    <div class="field-row" style="margin-top: 6px;">
                      <input
                        v-model="partsSearch"
                        class="field-input"
                        type="text"
                        placeholder="Поиск по названию или SKU"
                      >
                    </div>
                  </div>
                  <button
                    v-if="userRole === 'supervisor' || userRole === 'admin' || userRole === 'master'"
                    class="btn btn-primary"
                    type="button"
                    @click="openNewPartModal"
                  >
                    Новая запчасть
                  </button>
                </div>
                <div v-if="parts.length">
                  <table>
                    <thead>
                      <tr>
                        <th>Название</th>
                        <th>SKU</th>
                        <th>Цена</th>
                        <th>Остаток</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="p in filteredParts"
                        :key="p.uuid"
                      >
                        <td>{{ p.name }}</td>
                        <td>{{ p.sku || '—' }}</td>
                        <td>{{ p.price ?? '—' }}</td>
                        <td>{{ p.stock_qty ?? '—' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="empty-state">
                  Запчастей пока нет.
                </div>
              </div>
            </template>
          </div>
        </section>
      </main>
    </section>
    <!-- Модальное окно логина -->
    <div
      v-if="loginModalOpen"
      class="modal-backdrop"
      @click="closeAllModals"
    >
      <div
        class="modal"
        @click.stop
      >
        <form
          class="login-card"
          @submit.prevent="handleLogin"
        >
          <div class="field">
            <label class="field-label" for="modal-email">Email</label>
            <input
              id="modal-email"
              v-model="email"
              class="field-input"
              type="email"
              autocomplete="username"
              placeholder="admin@admin.ru"
              required
            >
          </div>

          <div class="field">
            <label class="field-label" for="modal-password">Пароль</label>
            <input
              id="modal-password"
              v-model="password"
              class="field-input"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              required
            >
          </div>

          <div class="hint">
            Данные используются только для получения токенов доступа.
          </div>

          <div v-if="loginError" class="error">
            {{ loginError }}
          </div>
          <div v-if="loginSuccess" class="success">
            Вход выполнен.
          </div>

          <div class="field">
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="isLoggingIn"
            >
              <span v-if="isLoggingIn" class="loader">
                <span class="loader-dot" />
                <span class="loader-dot" />
                <span class="loader-dot" />
              </span>
              <span v-else>Войти</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно создания клиента из заказа -->
    <div
      v-if="orderClientModal.open"
      class="modal-backdrop"
      @click="closeAllModals"
    >
      <div
        class="modal"
        @click.stop
      >
        <div class="login-card">
          <div class="field">
            <div class="field-label">
              Новый клиент
            </div>
          </div>
          <div class="field">
            <label class="field-label" for="modal-client-name">Имя</label>
            <input
              id="modal-client-name"
              v-model="orderClientModal.data.full_name"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-client-phone">Телефон</label>
            <input
              id="modal-client-phone"
              v-model="orderClientModal.data.phone"
              class="field-input"
              type="text"
              placeholder="+78008008000"
            >
            <div class="hint">
              Формат: +7 и 10 цифр, например +78008008000
            </div>
          </div>
          <div class="field">
            <label class="field-label" for="modal-client-email">Email</label>
            <input
              id="modal-client-email"
              v-model="orderClientModal.data.email"
              class="field-input"
              type="email"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-client-telegram">Telegram</label>
            <input
              id="modal-client-telegram"
              v-model="orderClientModal.data.telegram_nick"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-client-comment">Комментарий</label>
            <input
              id="modal-client-comment"
              v-model="orderClientModal.data.comment"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <button
              class="btn btn-primary"
              type="button"
              @click="submitOrderClientModal"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания устройства из заказа -->
    <div
      v-if="orderDeviceModal.open"
      class="modal-backdrop"
      @click="closeAllModals"
    >
      <div
        class="modal"
        @click.stop
      >
        <div class="login-card">
          <div class="field">
            <div class="field-label">
              Новое устройство
            </div>
          </div>
          <div class="field">
            <label class="field-label" for="modal-device-type">Тип устройства</label>
            <select
              id="modal-device-type"
              v-model="orderDeviceModal.data.type_uuid"
              class="field-input"
            >
              <option disabled value="">
                Выберите тип
              </option>
              <option
                v-for="dt in deviceTypes"
                :key="dt.uuid"
                :value="dt.uuid"
              >
                {{ dt.name }}
              </option>
            </select>
          </div>
          <div class="field">
            <label class="field-label" for="modal-device-brand">Бренд</label>
            <input
              id="modal-device-brand"
              v-model="orderDeviceModal.data.brand"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-device-model">Модель</label>
            <input
              id="modal-device-model"
              v-model="orderDeviceModal.data.model"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-device-serial">Серийный номер</label>
            <input
              id="modal-device-serial"
              v-model="orderDeviceModal.data.serial_number"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-device-description">Описание</label>
            <input
              id="modal-device-description"
              v-model="orderDeviceModal.data.description"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <button
              class="btn btn-primary"
              type="button"
              @click="submitOrderDeviceModal"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>


    <!-- Модальное окно новой запчасти -->
    <div
      v-if="newPartModal.open"
      class="modal-backdrop"
      @click="closeAllModals"
    >
      <div
        class="modal"
        @click.stop
      >
        <div class="login-card">
          <div class="field">
            <div class="field-label">
              Новая запчасть
            </div>
          </div>
          <div class="field">
            <label class="field-label" for="modal-part-name">Название</label>
            <input
              id="modal-part-name"
              v-model="newPartModal.data.name"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-part-sku">SKU</label>
            <input
              id="modal-part-sku"
              v-model="newPartModal.data.sku"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-part-price">Цена</label>
            <input
              id="modal-part-price"
              v-model.number="newPartModal.data.price"
              class="field-input"
              type="number"
              step="0.01"
            >
          </div>
          <div class="field">
            <label class="field-label" for="modal-part-stock">Остаток</label>
            <input
              id="modal-part-stock"
              v-model.number="newPartModal.data.stock_qty"
              class="field-input"
              type="number"
              min="0"
            >
          </div>
          <div class="field">
            <button
              class="btn btn-primary"
              type="button"
              @click="submitNewPartModal"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Попап: добавить работу к заказу -->
    <div
      v-if="addWorkModal.open"
      class="modal-backdrop"
      @click="closeAllModals"
    >
      <div
        class="modal"
        @click.stop
      >
        <div class="login-card">
          <div class="field-label">
            Добавить работу
          </div>
          <div class="field">
            <label class="field-label" for="mw-title">Название</label>
            <input
              id="mw-title"
              v-model="newWorkForm.title"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <label class="field-label" for="mw-price">Цена</label>
            <input
              id="mw-price"
              v-model.number="newWorkForm.price"
              class="field-input"
              type="number"
              step="0.01"
            >
          </div>
          <div class="field">
            <label class="field-label" for="mw-desc">Описание</label>
            <input
              id="mw-desc"
              v-model="newWorkForm.description"
              class="field-input"
              type="text"
            >
          </div>
          <div class="field">
            <button
              class="btn btn-primary"
              type="button"
              @click="addWorkToOrder"
            >
              Добавить работу
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Попап: добавить запчасть к заказу -->
    <div
      v-if="addPartToOrderModal.open"
      class="modal-backdrop"
      @click="closeAllModals"
    >
      <div
        class="modal"
        @click.stop
      >
        <div class="login-card">
          <div class="field-label">
            Добавить запчасть
          </div>
          <div class="field">
            <label class="field-label" for="mp-part">Запчасть</label>
            <div class="field-row">
              <input
                v-model="orderPartSearch"
                class="field-input"
                type="text"
                placeholder="Поиск по названию или SKU (от 3 символов)"
                @input="handleOrderPartSearchInput"
                @focus="handleOrderPartSearchInput"
              >
            </div>
            <div
              v-if="orderPartSuggestionsOpen && orderPartSearch.length >= 3"
              class="autocomplete-list"
            >
              <button
                v-for="p in partsForOrder"
                :key="p.uuid"
                type="button"
                class="autocomplete-item"
                @click="selectOrderPart(p)"
              >
                <div class="autocomplete-item-main">
                  {{ p.name }}
                </div>
                <div class="autocomplete-item-sub">
                  {{ p.sku || 'без SKU' }}
                </div>
              </button>
              <div
                v-if="!partsForOrder.length"
                class="autocomplete-empty"
              >
                Ничего не найдено
              </div>
            </div>
          </div>
          <div class="field">
            <label class="field-label" for="mp-qty">Кол-во</label>
            <input
              id="mp-qty"
              v-model.number="newOrderPartForm.qty"
              class="field-input"
              type="number"
              min="1"
            >
          </div>
          <div class="field">
            <label class="field-label" for="mp-price">Цена</label>
            <input
              id="mp-price"
              v-model.number="newOrderPartForm.price"
              class="field-input"
              type="number"
              step="0.01"
            >
          </div>
          <div class="field">
            <button
              class="btn btn-primary"
              type="button"
              @click="addPartToOrder"
            >
              Добавить запчасть
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue';
import {
  createClient,
  createDevice,
  createDeviceType,
  createEmployee,
  createOrder,
  createOrderPart,
  createPart,
  createPayment,
  createOrderComment,
  createWork,
  deleteClient,
  deleteEmployee,
  deleteOrder,
  getClients,
  getDevices,
  getDeviceTypes,
  getCurrentEmployee,
  getEmployees,
  getValidationRules,
  getOrderDetails,
  getOrderParts,
  getOrders,
  getParts,
  getPayments,
  getWorks,
  login,
  logout,
  registerUser,
  updateClient,
  updateEmployee,
  updateOrder,
} from './services/api';

const email = ref('');
const password = ref('');
const isLoggingIn = ref(false);
const loginError = ref('');
const loginSuccess = ref(false);
const accessToken = ref('');
const lastLoginEmail = ref('');
const loginModalOpen = ref(false);
const userRole = ref('other'); // supervisor | admin | manager | master | other
const currentEmployeeName = ref('');

const activeTab = ref('orders');
const clients = ref([]);
const orders = ref([]);
const devices = ref([]);
const deviceTypes = ref([]);
const parts = ref([]);
const works = ref([]);
const payments = ref([]);
const orderParts = ref([]);
const employees = ref([]);
const isLoading = ref(false);
const loadError = ref('');

const orderStatusFilter = ref([]);
const orderClientSearch = ref('');
const orderClientSuggestionsOpen = ref(false);
const orderPartSearch = ref('');
const orderPartSuggestionsOpen = ref(false);
const partsSearch = ref('');
const pendingOrderDevice = ref(null);
const detailsManagerId = ref(null);
const detailsEngineerId = ref(null);

const isAuthenticated = computed(() => !!accessToken.value);

const canManageEmployees = computed(() => userRole.value === 'supervisor');
const canCreateEmployees = computed(
  () => userRole.value === 'supervisor' || userRole.value === 'admin',
);

/** Правила валидации с бэкенда (Pydantic) — загружаются при старте */
const validationRules = ref(null);

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateEmailWithRules(val, rules) {
  const v = (val ?? '').trim();
  if (!v) return rules?.email?.message ?? 'Введите email';
  if (!EMAIL_RE.test(v)) return rules?.email?.message ?? 'Некорректный формат email';
  return '';
}

function validatePasswordWithRules(val, rules) {
  const v = val ?? '';
  if (!v) return rules?.password?.messages?.required ?? 'Введите пароль';
  const p = rules?.password;
  const msg = p?.messages;
  if (!p) return v.length < 6 ? 'Пароль не менее 6 символов' : '';
  if (v.length < p.min_length || v.length > p.max_length) return msg?.length ?? `Пароль от ${p.min_length} до ${p.max_length} символов`;
  if (!/\d/.test(v)) return msg?.digit ?? 'Пароль должен содержать хотя бы одну цифру';
  if (!/[A-Z]/.test(v)) return msg?.uppercase ?? 'Пароль должен содержать хотя бы одну заглавную букву';
  const special = p.special_characters ?? "!@#$%^&*(),.?\":{}|<>_-+[]=\\/";
  if (![...special].some((c) => v.includes(c))) return msg?.special ?? 'Пароль должен содержать хотя бы один спецсимвол';
  return '';
}

function normalizePhoneForValidation(val) {
  const cleaned = (val ?? '').replace(/[^\d+]/g, '');
  if (cleaned.startsWith('8') && cleaned.length === 11) return '+7' + cleaned.slice(1);
  return cleaned;
}

function validatePhoneWithRules(val, rules) {
  const v = (val ?? '').trim();
  if (!v) return '';
  const normalized = normalizePhoneForValidation(v);
  const pattern = rules?.phone?.pattern ?? '^\\+7\\d{10}$';
  if (!new RegExp(pattern).test(normalized)) return rules?.phone?.message ?? 'Not valid phone number. Expected format: +78008008000';
  return '';
}

const empEmailError = computed(() => {
  if (employeeForm.value.editMode) return '';
  return validateEmailWithRules(employeeForm.value.data?.email, validationRules.value);
});

const empPasswordError = computed(() => {
  if (employeeForm.value.editMode) return '';
  return validatePasswordWithRules(employeeForm.value.data?.password, validationRules.value);
});

const empPhoneError = computed(() => {
  return validatePhoneWithRules(employeeForm.value.data?.phone, validationRules.value);
});

const empFullNameError = computed(() => {
  const v = (employeeForm.value.data?.full_name ?? '').trim();
  if (!v) return validationRules.value?.full_name?.message ?? 'Введите ФИО';
  return '';
});

const employeeFormValid = computed(() => {
  if (!employeeForm.value.open) return false;
  const { editMode, data } = employeeForm.value;
  if (editMode) {
    return !empFullNameError.value && !empPhoneError.value;
  }
  return (
    !empEmailError.value &&
    !empPasswordError.value &&
    !empFullNameError.value &&
    !empPhoneError.value
  );
});

const orderFormValid = computed(() => {
  if (!orderForm.value.open) return false;
  const data = orderForm.value.data;

  if (orderForm.value.editMode) {
    // Для редактирования достаточно иметь статус (он всегда есть) — дополнительных полей не требуем.
    return !!data.status;
  }

  // Для создания заказа обязательно выбрать клиента и либо привязать устройство,
  // либо заполнить данные нового устройства (через «+ Новое»).
  return !!data.client_uuid && (!!data.device_uuid || !!pendingOrderDevice.value);
});

const orderCalculatedPrice = computed(() => {
  const d = orderDetails.value.data;
  if (!d) return 0;
  let total = 0;
  for (const w of d.works || []) {
    total += (w.price || 0) * (w.qty || 1);
  }
  for (const p of d.parts || []) {
    const unit = p.price ?? p.part_info?.price ?? 0;
    total += unit * (p.qty || 0);
  }
  return total;
});

const filteredOrders = computed(() => {
  if (!orderStatusFilter.value.length) {
    return orders.value;
  }
  return orders.value.filter((o) => orderStatusFilter.value.includes(o.status));
});

const clientsForOrder = computed(() => {
  const q = orderClientSearch.value.trim().toLowerCase();
  if (q.length < 3) {
    return clients.value;
  }
  return clients.value.filter((c) => {
    const name = (c.full_name || '').toLowerCase();
    const phone = (c.phone || '').toLowerCase();
    return name.includes(q) || phone.includes(q);
  });
});

const partsForOrder = computed(() => {
  const q = orderPartSearch.value.trim().toLowerCase();
  if (q.length < 3) {
    return parts.value;
  }
  return parts.value.filter((p) => {
    const name = (p.name || '').toLowerCase();
    const sku = (p.sku || '').toLowerCase();
    return name.includes(q) || sku.includes(q);
  });
});

const filteredParts = computed(() => {
  const q = partsSearch.value.trim().toLowerCase();
  if (!q) {
    return parts.value;
  }
  return parts.value.filter((p) => {
    const name = (p.name || '').toLowerCase();
    const sku = (p.sku || '').toLowerCase();
    return name.includes(q) || sku.includes(q);
  });
});

const currentCount = computed(() => {
  switch (activeTab.value) {
    case 'orders':
      return filteredOrders.value.length;
    case 'employees':
      return employees.value.length;
    case 'parts':
      return parts.value.length;
    default:
      return 0;
  }
});

const devicesForSelectedClient = computed(() => {
  if (!orderForm.value.data.client_uuid) {
    return devices.value;
  }
  const client = clients.value.find((c) => c.uuid === orderForm.value.data.client_uuid);
  if (!client) {
    return devices.value;
  }
  return devices.value.filter((d) => d.client_id === client.id);
});

function clientLabel(id) {
  const c = clients.value.find((client) => client.id === id);
  if (!c) {
    return id ? `Клиент #${id}` : '—';
  }
  return c.full_name || `Клиент #${id}`;
}

function deviceLabel(id) {
  const d = devices.value.find((device) => device.id === id);
  if (!d) {
    return id ? `Устройство #${id}` : '—';
  }
  return `${d.brand} ${d.model}`;
}

function employeeLabel(id) {
  const e = employees.value.find((emp) => emp.id === id);
  if (!e) {
    return id ? `Сотрудник #${id}` : '—';
  }
  return e.full_name;
}

const clientForm = ref({
  open: false,
  editMode: false,
  uuid: null,
  data: {
    full_name: '',
    phone: '',
    email: '',
    telegram_nick: '',
    comment: '',
  },
});

const orderForm = ref({
  open: false,
  editMode: false,
  uuid: null,
  data: {
    client_uuid: '',
    device_uuid: '',
    manager_uuid: '',
    assigned_employee_uuid: '',
    status: 'new',
    price: null,
    problem_description: '',
    comment: '',
  },
});

const deviceForm = ref({
  open: false,
  data: {
    client_uuid: '',
    type_uuid: '',
    brand: '',
    model: '',
    serial_number: '',
    description: '',
  },
});

const deviceTypeForm = ref({
  open: false,
  data: {
    name: '',
    description: '',
  },
});

const partForm = ref({
  open: false,
  data: {
    name: '',
    sku: '',
    price: null,
    stock_qty: null,
  },
});

const workForm = ref({
  open: false,
  data: {
    order_uuid: '',
    title: '',
    employee_uuid: '',
    description: '',
    price: null,
  },
});

const paymentForm = ref({
  open: false,
  data: {
    order_uuid: '',
    amount: null,
    payment_method: '',
    employee_uuid: '',
    comment: '',
  },
});

const orderPartForm = ref({
  open: false,
  data: {
    order_uuid: '',
    part_uuid: '',
    qty: 1,
    price: null,
  },
});

const orderClientModal = ref({
  open: false,
  data: {
    full_name: '',
    phone: '',
    email: '',
    telegram_nick: '',
    comment: '',
  },
});

const orderDeviceModal = ref({
  open: false,
  data: {
    type_uuid: '',
    brand: '',
    model: '',
    serial_number: '',
    description: '',
  },
});

const employeeForm = ref({
  open: false,
  editMode: false,
  uuid: null,
  data: {
    email: '',
    password: '',
    full_name: '',
    phone: '',
    position: 'master',
  },
});

const ORDER_STATUS_OPTIONS = [
  { value: 'new', label: 'Новый' },
  { value: 'accepted', label: 'Принят в работу' },
  { value: 'diagnostics', label: 'На диагностике' },
  { value: 'on_approval', label: 'На согласовании' },
  { value: 'waiting_parts', label: 'Ждём запчасти' },
  { value: 'in_repair', label: 'В ремонте' },
  { value: 'paid', label: 'Оплачен' },
  { value: 'closed', label: 'Закрыт' },
  { value: 'rejected', label: 'Отказ' },
];

const orderDetails = ref({
  loading: false,
  data: null,
});

const newWorkForm = ref({
  title: '',
  employee_uuid: '',
  description: '',
  price: null,
});

const newOrderPartForm = ref({
  part_uuid: '',
  qty: 1,
  price: null,
});

const addWorkModal = ref({ open: false });
const addPartToOrderModal = ref({ open: false });
const newCommentText = ref('');
const commentsListRef = ref(null);

const newPartModal = ref({
  open: false,
  data: {
    name: '',
    sku: '',
    price: null,
    stock_qty: null,
  },
});

async function loadData() {
  if (!isAuthenticated.value) {
    return;
  }

  isLoading.value = true;
  loadError.value = '';

  try {
    switch (activeTab.value) {
      case 'orders': {
        if (userRole.value === 'supervisor' || userRole.value === 'admin') {
          const [ordersData, clientsData, devicesData, employeesData] = await Promise.all([
            getOrders(),
            getClients(),
            getDevices(),
            getEmployees(),
          ]);
          orders.value = ordersData;
          clients.value = clientsData;
          devices.value = devicesData;
          employees.value = employeesData;
        } else {
          const [ordersData, clientsData, devicesData] = await Promise.all([
            getOrders(),
            getClients(),
            getDevices(),
          ]);
          orders.value = ordersData;
          clients.value = clientsData;
          devices.value = devicesData;
          employees.value = [];
        }
        break;
      }
      case 'employees':
        employees.value = await getEmployees();
        break;
      case 'parts':
        parts.value = await getParts();
        break;
      default:
        break;
    }
  } catch (e) {
    // Show a compact, user-friendly error
    const message = e?.response?.data?.detail || e?.message || 'Не удалось загрузить данные.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось загрузить данные.';
  } finally {
    isLoading.value = false;
  }
}

async function handleLogin() {
  loginError.value = '';
  loginSuccess.value = false;
  isLoggingIn.value = true;

  try {
    const data = await login(email.value, password.value);
    accessToken.value = data.access_token;
    lastLoginEmail.value = email.value;
    await refreshUserRole();
    loginSuccess.value = true;
    loginModalOpen.value = false;
    await loadData();
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка авторизации.';
    loginError.value = typeof message === 'string' ? message : 'Ошибка авторизации.';
  } finally {
    isLoggingIn.value = false;
  }
}

async function handleLogout() {
  await logout();
  accessToken.value = '';
  clients.value = [];
  orders.value = [];
  devices.value = [];
  deviceTypes.value = [];
  parts.value = [];
  works.value = [];
  payments.value = [];
  orderParts.value = [];
  employees.value = [];
}

function openLoginModal() {
  loginError.value = '';
  loginSuccess.value = false;
  loginModalOpen.value = true;
}

/** Берёт роль из API (position текущего сотрудника). */
async function refreshUserRole() {
  if (!accessToken.value) {
    userRole.value = 'other';
    return;
  }
  try {
    const me = await getCurrentEmployee();
    const pos = (me?.position || '').toLowerCase();
    currentEmployeeName.value = me?.full_name || '';
    if (pos === 'supervisor') userRole.value = 'supervisor';
    else if (pos === 'admin') userRole.value = 'admin';
    else if (pos === 'manager') userRole.value = 'manager';
    else if (pos === 'master') userRole.value = 'master';
    else userRole.value = 'other';
    window.localStorage.setItem('user_role', userRole.value);
  } catch {
    userRole.value = 'other';
    window.localStorage.setItem('user_role', userRole.value);
  }
}

function closeAllModals() {
  loginModalOpen.value = false;
  orderClientModal.value.open = false;
  orderDeviceModal.value.open = false;
  newPartModal.value.open = false;
  addWorkModal.value.open = false;
  addPartToOrderModal.value.open = false;
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    if (loginModalOpen.value || orderClientModal.value.open || orderDeviceModal.value.open || newPartModal.value.open || addWorkModal.value.open || addPartToOrderModal.value.open) {
      event.preventDefault();
      closeAllModals();
    }
  }
}

function formatDate(value) {
  if (!value) return '—';

  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString('ru-RU', {
      year: '2-digit',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(value);
  }
}

function orderStatusLabel(value) {
  const found = ORDER_STATUS_OPTIONS.find((s) => s.value === value);
  return found ? found.label : (value || '—');
}

function orderStatusClass(value) {
  switch (value) {
    case 'new':
    case 'accepted':
    case 'diagnostics':
      return 'badge--status-green';
    case 'on_approval':
    case 'waiting_parts':
    case 'in_repair':
      return 'badge--status-yellow';
    case 'paid':
      return 'badge--status-blue';
    case 'closed':
      return 'badge--status-red';
    case 'rejected':
      return 'badge--status-black';
    default:
      return 'badge--status-muted';
  }
}

function tableStatusFilterClass(value) {
  switch (value) {
    case 'new':
    case 'accepted':
    case 'diagnostics':
      return 'table-status-filter-pill--green';
    case 'on_approval':
    case 'waiting_parts':
    case 'in_repair':
      return 'table-status-filter-pill--yellow';
    case 'paid':
      return 'table-status-filter-pill--blue';
    case 'closed':
      return 'table-status-filter-pill--red';
    case 'rejected':
      return 'table-status-filter-pill--black';
    default:
      return '';
  }
}

function handleOrderClientSearchInput() {
  const q = orderClientSearch.value.trim();
  orderClientSuggestionsOpen.value = q.length >= 3;
  // При изменении строки поиска сбрасываем выбранного клиента,
  // чтобы пользователь явно подтвердил выбор из подсказок.
  orderForm.value.data.client_uuid = '';
}

function selectOrderClient(client) {
  orderForm.value.data.client_uuid = client.uuid;
  orderClientSearch.value = `${client.full_name} (${client.phone || '—'})`;
  orderClientSuggestionsOpen.value = false;
}

function handleOrderPartSearchInput() {
  const q = orderPartSearch.value.trim();
  orderPartSuggestionsOpen.value = q.length >= 3;
  newOrderPartForm.value.part_uuid = '';
}

function selectOrderPart(part) {
  newOrderPartForm.value.part_uuid = part.uuid;
  orderPartSearch.value = `${part.name} (${part.sku || 'без SKU'})`;
  orderPartSuggestionsOpen.value = false;
}

function toggleOrderStatusFilter(value) {
  const idx = orderStatusFilter.value.indexOf(value);
  if (idx === -1) {
    orderStatusFilter.value = [...orderStatusFilter.value, value];
  } else {
    orderStatusFilter.value = orderStatusFilter.value.filter((v) => v !== value);
  }
}

function clearOrderStatusFilter() {
  orderStatusFilter.value = [];
}

function changeTab(tab) {
  // Если уже на вкладке заказов и открыта деталка — по повторному нажатию «Заказы» вернёмся к списку
  if (tab === 'orders' && activeTab.value === 'orders' && orderDetails.value.data) {
    orderDetails.value = { loading: false, data: null };
    loadData();
    return;
  }

  activeTab.value = tab;
  loadData();
}

function resetForm(formRef, initial) {
  formRef.value.open = false;
  formRef.value.editMode = false;
  formRef.value.uuid = null;
  formRef.value.data = { ...initial };
}

function startCreateClient() {
  clientForm.value.open = true;
  clientForm.value.editMode = false;
  clientForm.value.uuid = null;
  clientForm.value.data = {
    full_name: '',
    phone: '',
    email: '',
    telegram_nick: '',
    comment: '',
  };
}

function startEditClient(client) {
  clientForm.value.open = true;
  clientForm.value.editMode = true;
  clientForm.value.uuid = client.uuid;
  clientForm.value.data = {
    full_name: client.full_name,
    phone: client.phone,
    email: client.email,
    telegram_nick: client.telegram_nick,
    comment: client.comment,
  };
}

async function submitClientForm() {
  try {
    if (clientForm.value.editMode && clientForm.value.uuid) {
      await updateClient(clientForm.value.uuid, clientForm.value.data);
    } else {
      await createClient(clientForm.value.data);
    }
    await loadData();
    clientForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения клиента.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения клиента.';
  }
}

async function removeClient(client) {
  if (!window.confirm(`Удалить клиента ${client.full_name}?`)) return;
  try {
    await deleteClient(client.uuid);
    await loadData();
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка удаления клиента.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка удаления клиента.';
  }
}

function startCreateClientForOrder() {
  orderClientModal.value.open = true;
  orderClientModal.value.data = {
    full_name: '',
    phone: '',
    email: '',
    telegram_nick: '',
    comment: '',
  };
}

async function submitOrderClientModal() {
  try {
    const created = await createClient(orderClientModal.value.data);
    clients.value = await getClients();
    if (created?.uuid) {
      orderForm.value.data.client_uuid = created.uuid;
    }
    orderClientModal.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка создания клиента.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка создания клиента.';
  }
}

async function ensureOrderReferences() {
  try {
    if (!clients.value.length) {
      clients.value = await getClients();
    }
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось загрузить справочные данные.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось загрузить справочные данные.';
  }
}

async function startCreateOrder() {
  await ensureOrderReferences();
  orderForm.value.open = true;
  orderForm.value.editMode = false;
  orderForm.value.uuid = null;
  pendingOrderDevice.value = null;
  orderForm.value.data = {
    client_uuid: '',
    device_uuid: '',
    manager_uuid: '',
    assigned_employee_uuid: '',
    status: 'new',
    price: null,
    problem_description: '',
    comment: '',
  };
}

function startEditOrder(order) {
  orderForm.value.open = true;
  orderForm.value.editMode = true;
  orderForm.value.uuid = order.uuid;
  orderForm.value.data = {
    status: order.status,
    price: order.price,
    problem_description: order.problem_description,
    comment: order.comment,
  };
}

async function submitOrderForm() {
  try {
    if (orderForm.value.editMode && orderForm.value.uuid) {
      await updateOrder(orderForm.value.uuid, {
        status: orderForm.value.data.status,
        price: orderForm.value.data.price,
        problem_description: orderForm.value.data.problem_description,
        comment: orderForm.value.data.comment,
      });
    } else {
      // Создание нового заказа: при необходимости сначала создаём устройство.
      let deviceUuid = orderForm.value.data.device_uuid;
      if (!deviceUuid && pendingOrderDevice.value) {
        const devicePayload = {
          client_uuid: orderForm.value.data.client_uuid,
          type_uuid: pendingOrderDevice.value.type_uuid,
          brand: pendingOrderDevice.value.brand,
          model: pendingOrderDevice.value.model,
          serial_number: pendingOrderDevice.value.serial_number,
          description: pendingOrderDevice.value.description,
        };
        const createdDevice = await createDevice(devicePayload);
        devices.value = await getDevices();
        deviceUuid = createdDevice?.uuid;
        orderForm.value.data.device_uuid = deviceUuid || '';
      }

      const payload = {
        ...orderForm.value.data,
        device_uuid: deviceUuid,
      };
      // Менеджер указывается только если создаёт не менеджер и явно выбран.
      if (userRole.value !== 'manager' && payload.manager_uuid) {
        // оставляем выбранного менеджера
      } else {
        delete payload.manager_uuid;
      }

      await createOrder(payload);
    }
    await loadData();
    orderForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения заказа.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения заказа.';
  }
}

async function removeOrder(order) {
  if (!window.confirm(`Удалить заказ #${order.id}?`)) return;
  try {
    await deleteOrder(order.uuid);
    await loadData();
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка удаления заказа.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка удаления заказа.';
  }
}

async function openOrderDetails(order) {
  try {
    orderDetails.value.loading = true;
    if (userRole.value === 'supervisor' || userRole.value === 'admin') {
      const [details, partsData, employeesData] = await Promise.all([
        getOrderDetails(order.uuid),
        getParts(),
        getEmployees(),
      ]);
      orderDetails.value.data = details;
      parts.value = partsData;
      employees.value = employeesData;
      detailsManagerId.value = details.creator?.id ?? null;
      detailsEngineerId.value = details.assigned_employee?.id ?? null;
    } else {
      const [details, partsData] = await Promise.all([
        getOrderDetails(order.uuid),
        getParts(),
      ]);
      orderDetails.value.data = details;
      parts.value = partsData;
    }
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось загрузить детали заказа.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось загрузить детали заказа.';
  } finally {
    orderDetails.value.loading = false;
  }
}

function startCreateDevice() {
  deviceForm.value.open = true;
  deviceForm.value.data = {
    client_uuid: '',
    type_uuid: '',
    brand: '',
    model: '',
    serial_number: '',
    description: '',
  };
}

async function submitDeviceForm() {
  try {
    await createDevice(deviceForm.value.data);
    await loadData();
    deviceForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения устройства.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения устройства.';
  }
}

async function startCreateDeviceForOrder() {
  if (!orderForm.value.data.client_uuid) {
    // Нельзя создавать устройство без выбранного клиента
    loadError.value = 'Сначала выберите клиента для заказа.';
    return;
  }

  try {
    if (!deviceTypes.value.length) {
      deviceTypes.value = await getDeviceTypes();
    }
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось загрузить типы устройств.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось загрузить типы устройств.';
    return;
  }

  orderDeviceModal.value.open = true;
  orderDeviceModal.value.data = {
    type_uuid: '',
    brand: '',
    model: '',
    serial_number: '',
    description: '',
  };
}

async function submitOrderDeviceModal() {
  try {
    // Только сохраняем данные устройства, а сам девайс создаём при сохранении заказа.
    pendingOrderDevice.value = {
      type_uuid: orderDeviceModal.value.data.type_uuid,
      brand: orderDeviceModal.value.data.brand,
      model: orderDeviceModal.value.data.model,
      serial_number: orderDeviceModal.value.data.serial_number,
      description: orderDeviceModal.value.data.description,
    };
    orderDeviceModal.value.open = false;
  } catch (e) {
    const message = e?.message || 'Ошибка заполнения устройства.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка заполнения устройства.';
  }
}

function startCreateDeviceType() {
  deviceTypeForm.value.open = true;
  deviceTypeForm.value.data = {
    name: '',
    description: '',
  };
}

async function submitDeviceTypeForm() {
  try {
    await createDeviceType(deviceTypeForm.value.data);
    await loadData();
    deviceTypeForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения типа устройства.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения типа устройства.';
  }
}

function openNewPartModal() {
  newPartModal.value.open = true;
  newPartModal.value.data = {
    name: '',
    sku: '',
    price: null,
    stock_qty: null,
  };
}

function startCreateWork() {
  workForm.value.open = true;
  workForm.value.data = {
    order_uuid: '',
    title: '',
    employee_uuid: '',
    description: '',
    price: null,
  };
}

async function submitWorkForm() {
  try {
    await createWork(workForm.value.data);
    await loadData();
    workForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения работы.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения работы.';
  }
}

function startCreatePayment() {
  paymentForm.value.open = true;
  paymentForm.value.data = {
    order_uuid: '',
    amount: null,
    payment_method: '',
    employee_uuid: '',
    comment: '',
  };
}

async function submitPaymentForm() {
  try {
    await createPayment(paymentForm.value.data);
    await loadData();
    paymentForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения платежа.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения платежа.';
  }
}

function startCreateOrderPart() {
  orderPartForm.value.open = true;
  orderPartForm.value.data = {
    order_uuid: '',
    part_uuid: '',
    qty: 1,
    price: null,
  };
}

async function submitOrderPartForm() {
  try {
    await createOrderPart(orderPartForm.value.data);
    await loadData();
    orderPartForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения запчасти в заказе.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения запчасти в заказе.';
  }
}

function startCreateEmployee() {
  employeeForm.value.open = true;
  employeeForm.value.editMode = false;
  employeeForm.value.uuid = null;
  employeeForm.value.data = {
    email: '',
    password: '',
    full_name: '',
    phone: '',
    position: 'master',
  };
}

function startEditEmployee(employee) {
  employeeForm.value.open = true;
  employeeForm.value.editMode = true;
  employeeForm.value.uuid = employee.uuid;
  employeeForm.value.data = {
    email: '',
    password: '',
    full_name: employee.full_name,
    phone: employee.phone || '',
    position: employee.position,
  };
}

async function submitEmployeeForm() {
  try {
    if (employeeForm.value.editMode && employeeForm.value.uuid) {
      await updateEmployee(employeeForm.value.uuid, {
        full_name: employeeForm.value.data.full_name,
        phone: employeeForm.value.data.phone,
        position: employeeForm.value.data.position,
      });
    } else {
      const registration = await registerUser(
        employeeForm.value.data.email,
        employeeForm.value.data.password,
      );
      const userUuid = registration.uuid;
      await createEmployee({
        user_uuid: userUuid,
        full_name: employeeForm.value.data.full_name,
        phone: employeeForm.value.data.phone,
        position: employeeForm.value.data.position,
      });
    }
    employees.value = await getEmployees();
    employeeForm.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения сотрудника.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения сотрудника.';
  }
}

async function removeEmployee(employee) {
  if (!window.confirm(`Удалить сотрудника ${employee.full_name}?`)) return;
  try {
    await deleteEmployee(employee.uuid);
    employees.value = await getEmployees();
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка удаления сотрудника.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка удаления сотрудника.';
  }
}

async function saveOrderDetails() {
  if (!orderDetails.value.data) return;
  try {
    await updateOrder(orderDetails.value.data.uuid, {
      status: orderDetails.value.data.status,
      price: orderCalculatedPrice.value,
      problem_description: orderDetails.value.data.problem_description,
    });
    const updated = await getOrderDetails(orderDetails.value.data.uuid);
    orderDetails.value.data = updated;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось сохранить заказ.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось сохранить заказ.';
  }
}

function openAddWorkModal() {
  addWorkModal.value.open = true;
}

function openAddPartToOrderModal() {
  addPartToOrderModal.value.open = true;
}

function formatCommentDate(value) {
  if (!value) return '—';
  try {
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
  } catch {
    return String(value);
  }
}

async function sendOrderComment() {
  if (!orderDetails.value.data || !newCommentText.value.trim()) return;
  try {
    await createOrderComment({
      order_uuid: orderDetails.value.data.uuid,
      text: newCommentText.value.trim(),
    });
    const updated = await getOrderDetails(orderDetails.value.data.uuid);
    orderDetails.value.data = updated;
    newCommentText.value = '';
    await nextTick();
    if (commentsListRef.value) {
      commentsListRef.value.scrollTop = commentsListRef.value.scrollHeight;
    }
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось отправить комментарий.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось отправить комментарий.';
  }
}

async function addWorkToOrder() {
  if (!orderDetails.value.data || !newWorkForm.value.title) return;
  try {
    const payload = {
      order_uuid: orderDetails.value.data.uuid,
      title: newWorkForm.value.title,
      description: newWorkForm.value.description || undefined,
      price: newWorkForm.value.price || undefined,
      // Исполнитель работы — инженер, назначенный у заказа.
      employee_uuid: orderDetails.value.data.assigned_employee?.uuid || undefined,
    };
    await createWork(payload);
    const updated = await getOrderDetails(orderDetails.value.data.uuid);
    orderDetails.value.data = updated;
    newWorkForm.value = { title: '', employee_uuid: '', description: '', price: null };
    addWorkModal.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось добавить работу.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось добавить работу.';
  }
}

async function addPartToOrder() {
  if (!orderDetails.value.data || !newOrderPartForm.value.part_uuid || !newOrderPartForm.value.qty) return;
  try {
    const payload = {
      order_uuid: orderDetails.value.data.uuid,
      part_uuid: newOrderPartForm.value.part_uuid,
      qty: newOrderPartForm.value.qty,
      price: newOrderPartForm.value.price || undefined,
    };
    await createOrderPart(payload);
    const [updatedOrder, partsData] = await Promise.all([
      getOrderDetails(orderDetails.value.data.uuid),
      getParts(),
    ]);
    orderDetails.value.data = updatedOrder;
    parts.value = partsData;
    newOrderPartForm.value = { part_uuid: '', qty: 1, price: null };
    addPartToOrderModal.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось добавить запчасть.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось добавить запчасть.';
  }
}

async function decrementWork(work) {
  if (!orderDetails.value.data) return;
  try {
    if ((work.qty || 1) > 1) {
      await updateWork(work.uuid, {
        qty: (work.qty || 1) - 1,
      });
    } else {
      await deleteWork(work.uuid);
    }

    const updated = await getOrderDetails(orderDetails.value.data.uuid);
    orderDetails.value.data = updated;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось обновить работу.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось обновить работу.';
  }
}

async function decrementOrderPart(orderPart) {
  if (!orderDetails.value.data) return;
  try {
    if ((orderPart.qty || 0) > 1) {
      await updateOrderPart(orderPart.uuid, {
        qty: orderPart.qty - 1,
      });
    } else {
      await deleteOrderPart(orderPart.uuid);
    }

    const [updatedOrder, partsData] = await Promise.all([
      getOrderDetails(orderDetails.value.data.uuid),
      getParts(),
    ]);
    orderDetails.value.data = updatedOrder;
    parts.value = partsData;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Не удалось обновить запчасть в заказе.';
    loadError.value = typeof message === 'string' ? message : 'Не удалось обновить запчасть в заказе.';
  }
}

async function submitNewPartModal() {
  try {
    const created = await createPart(newPartModal.value.data);
    const partsData = await getParts();
    parts.value = partsData;
    if (created?.uuid) {
      newOrderPartForm.value.part_uuid = created.uuid;
    }
    newPartModal.value.open = false;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка сохранения запчасти.';
    loadError.value = typeof message === 'string' ? message : 'Ошибка сохранения запчасти.';
  }
}

onMounted(async () => {
  accessToken.value = window.localStorage.getItem('access_token') || '';
  lastLoginEmail.value = window.localStorage.getItem('last_login_email') || '';
  getValidationRules()
    .then((rules) => { validationRules.value = rules; })
    .catch(() => {});
  if (accessToken.value) {
    await refreshUserRole();
    loadData();
  }
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

