<template>
  <div>
    <div class="page-head">
      <div>
        <span class="eyebrow">Administration</span>
        <h1>Experiments</h1>
      </div>
      <span class="count">{{ experiments.length }} configured</span>
    </div>

    <p class="config-note">
      These experiments are baked into the dashboard at build time. To add or
      change one, edit <code>vue-frontend/src/config.json</code> in the repository
      and redeploy. A session is matched to an experiment by its
      <b>session&nbsp;name</b>.
    </p>

    <div v-if="experiments.length" class="experiment-grid">
      <div v-for="exp in experiments" :key="exp.name" class="panel experiment-card">
        <h2 class="panel-title">{{ exp.name }}</h2>

        <div class="exp-meta">
          <span class="tag">{{ exp.actions.length }} actions</span>
          <span class="tag">{{ exp.receivers.length }} receivers</span>
          <span class="tag">{{ exp.levels.length }} levels</span>
        </div>

        <!-- Implemented actions -->
        <section class="exp-section">
          <h3 class="exp-section-title">Actions</h3>
          <ul class="action-list">
            <li v-for="(action, i) in exp.actions" :key="action.title + '_' + i" class="action-item">
              <div class="action-head">
                <span class="action-title">{{ action.title }}</span>
                <code class="action-event">{{ action.eventName }}</code>
              </div>
              <div class="action-tags">
                <span v-if="action.requiresInput" class="tag">input</span>
                <span
                  v-for="ctx in action.contexts"
                  :key="ctx"
                  class="tag idle"
                ><span class="dot"></span>{{ ctx }}</span>
                <span v-if="action.params" class="action-params">{{ action.params }}</span>
              </div>
            </li>
          </ul>
        </section>

        <!-- Receivers -->
        <section v-if="exp.receivers.length" class="exp-section">
          <h3 class="exp-section-title">Receivers</h3>
          <div class="chip-row">
            <span v-for="r in exp.receivers" :key="r.key" class="chip">
              {{ r.key }}<small>×{{ r.maxHistory }}</small>
            </span>
          </div>
        </section>

        <!-- Levels -->
        <section v-if="exp.levels.length" class="exp-section">
          <h3 class="exp-section-title">Levels</h3>
          <div class="chip-row">
            <span v-for="lvl in exp.levels" :key="lvl" class="chip">{{ lvl }}</span>
          </div>
        </section>
      </div>
    </div>

    <div v-else class="empty-state">
      <span class="glyph">⊘</span>
      <p>No experiments configured</p>
    </div>
  </div>
</template>

<script>
  import config from '@/config.json';

  export default {
    name: 'configedit',
    computed: {
      experiments() {
        const apps = config.applications || {};
        return Object.entries(apps).map(([name, app]) => ({
          name,
          actions: (app.controlButtons || []).map((button) => {
            const params = button.payload?.parameters || {};
            const hasParams = Object.keys(params).length > 0;
            return {
              title: button.title,
              eventName: button.payload?.eventName || '—',
              requiresInput: !!button.requiresInput,
              contexts: Array.isArray(button.context) ? button.context : [],
              params: hasParams ? JSON.stringify(params) : null,
            };
          }),
          receivers: this.flattenReceivers(app.receivers),
          levels: this.flattenLevels(app.levels),
        }));
      },
    },
    methods: {
      flattenReceivers(receivers) {
        const out = [];
        for (const group of receivers || []) {
          for (const [key, meta] of Object.entries(group || {})) {
            out.push({ key, maxHistory: meta?.maxHistory ?? 10 });
          }
        }
        return out;
      },
      flattenLevels(levels) {
        const out = [];
        for (const group of levels || []) {
          for (const id of Object.keys(group || {})) out.push(id);
        }
        return out;
      },
    },
  };
</script>

<style scoped>
.config-note {
  max-width: 1000px;
  margin: 0 0 var(--csl-s-6);
  font-family: var(--csl-font-mono);
  font-size: 13px;
  line-height: 1.7;
  color: var(--csl-fg-3);
}

.config-note code {
  color: var(--csl-cyan);
}

.config-note b {
  color: var(--csl-magenta);
}

.experiment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(380px, 100%), 1fr));
  gap: var(--csl-s-6);
  align-items: start;
}

/* On phones, let the action title + event name stack instead of overflowing */
@media (max-width: 560px) {
  .action-head {
    flex-direction: column;
    gap: 4px;
  }

  .action-event {
    white-space: normal;
    word-break: break-word;
  }
}

.exp-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--csl-s-2);
  margin-bottom: var(--csl-s-5);
}

.exp-section {
  margin-top: var(--csl-s-5);
}

.exp-section-title {
  margin: 0 0 var(--csl-s-3);
  font-family: var(--csl-font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--csl-fg-3);
}

.action-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--csl-s-2);
}

.action-item {
  border: 1px solid var(--csl-line);
  border-radius: var(--csl-r-2);
  background: color-mix(in srgb, var(--csl-panel) 45%, transparent);
  padding: 10px 13px;
}

.action-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--csl-s-3);
}

.action-title {
  font-family: var(--csl-font-heading);
  font-weight: 700;
  font-size: 15px;
  color: var(--csl-fg-1);
}

.action-event {
  font-family: var(--csl-font-mono);
  font-size: 12px;
  color: var(--csl-cyan);
  white-space: nowrap;
}

.action-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.action-params {
  font-family: var(--csl-font-mono);
  font-size: 11px;
  color: var(--csl-fg-3);
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  font-family: var(--csl-font-mono);
  font-size: 12px;
  color: var(--csl-fg-2);
  border: 1px solid var(--csl-line-strong);
  border-radius: var(--csl-r-1);
  padding: 4px 9px;
  background: color-mix(in srgb, var(--csl-panel) 45%, transparent);
}

.chip small {
  color: var(--csl-fg-4);
  font-size: 10px;
}
</style>
