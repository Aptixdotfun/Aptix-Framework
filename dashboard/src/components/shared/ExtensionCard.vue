<script setup lang="ts">
const props = defineProps({
  title: String,
  link: String,
  logo: String
});

const open = (link: string | undefined) => {
  window.open(link, '_blank');
};
</script>

<template>
  <v-card variant="outlined" elevation="0" class="withbg">
    <v-card-item style="padding: 10px 12px">
      <div class="d-sm-flex align-center justify-space-between">
        <img v-if="logo" :src="logo" alt="logo" style="width: 40px; height: 40px; margin-right: 8px;">
        <v-card-title style="font-size: 16px;">{{ props.title }}</v-card-title>
        <v-spacer></v-spacer>
        <v-btn size="small" text="Read" variant="flat" border  @click="open(props.link)">帮助</v-btn>
      </div>
    </v-card-item>
    <v-divider></v-divider>
    <v-card-text style="padding: 16px;">
      <slot />
    </v-card-text>
  </v-card>
</template>
