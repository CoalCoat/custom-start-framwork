using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using HarmonyLib;
using Il2Cpp;
using Il2CppSystem.Collections.Generic;
using Il2CppTMPro;
using UnityEngine;

namespace CustomStartFramework
{
    [HarmonyPatch(typeof(StartingPerkList), "InitStartingPerk")]
    internal static class InitStartingPerkPatch
    {
        private static void Postfix()
        {
            CustomStartPerkUi.EnsureRegistered();
        }
    }

    [HarmonyPatch(typeof(PerkUIController), "OpenUI")]
    internal static class PerkPickerPatch
    {
        private static void Postfix(PerkUIController __instance)
        {
            CustomStartPerkUi.EnsurePicker(__instance);
            CustomStartPerkUi.OnPickerOpened(__instance);
        }
    }

    [HarmonyPatch(typeof(PerkUIController), "OnChange")]
    internal static class PerkSelectionChangePatch
    {
        private static void Postfix(PerkUIController __instance)
        {
            CustomStartPerkUi.SyncExtraSlots(__instance);
        }
    }

    [HarmonyPatch(typeof(StartingPerk), "GetLocalizedDisplayName")]
    internal static class PerkNamePatch
    {
        private static void Postfix(StartingPerk __instance, ref string __result)
        {
            CustomStartProfile profile = CustomStartPerkRegistry.Find(__instance?.id);
            if (profile?.Name != null)
                __result = profile.Name.Pick();
        }
    }

    [HarmonyPatch(typeof(StartingPerk), "GetLocalizedDescription")]
    internal static class PerkDescriptionPatch
    {
        private static void Postfix(StartingPerk __instance, ref string __result)
        {
            CustomStartProfile profile = CustomStartPerkRegistry.Find(__instance?.id);
            if (profile?.Description != null)
                __result = profile.Description.Pick();
        }
    }

    [HarmonyPatch(typeof(StartingPerkIconLoader), "Start")]
    internal static class IconInjectionPatch
    {
        private static void Postfix()
        {
            PerkIconLoader.InjectAll();
        }
    }

    [HarmonyPatch(typeof(StartingPerkElement), "Start")]
    internal static class PerkElementStartPatch
    {
        private static void Postfix(StartingPerkElement __instance)
        {
            CustomStartProfile profile = CustomStartPerkRegistry.Find(__instance?.id);
            if (profile != null)
                CustomStartPerkUi.ApplyCustomPerkElement(__instance, profile);
        }
    }

    internal static class CustomStartPerkUi
    {
        private const int ExtraSlotsPerCustomPerk = 1;

        private static int extraApplied;

        private static readonly System.Collections.Generic.Dictionary<string, StartingPerk> Created =
            new System.Collections.Generic.Dictionary<string, StartingPerk>(StringComparer.Ordinal);

        internal static void OnPickerOpened(PerkUIController ui)
        {
            extraApplied = 0;
            SyncExtraSlots(ui);
        }

        internal static void SyncExtraSlots(PerkUIController ui)
        {
            if (ui == null)
                return;

            int desired = CountSelectedCustomPerks(ui) * ExtraSlotsPerCustomPerk;
            int delta = desired - extraApplied;
            if (delta != 0)
            {
                ui.maxPerkCount += delta;
                extraApplied = desired;
            }
            RefreshSlotCounter(ui);
        }

        private static int CountSelectedCustomPerks(PerkUIController ui)
        {
            if (ui.selectedPerks == null)
                return 0;

            int count = 0;
            foreach (StartingPerkElement element in ui.selectedPerks.GetComponentsInChildren<StartingPerkElement>(true))
            {
                if (element != null && CustomStartPerkRegistry.Find(element.id) != null)
                    count++;
            }
            return count;
        }

        private static void RefreshSlotCounter(PerkUIController ui)
        {
            TextMeshProUGUI slotCounter = ui.slotCounter;
            if (slotCounter == null)
                return;

            string text = slotCounter.text;
            if (string.IsNullOrEmpty(text))
                return;

            Match match = Regex.Match(text, "\\d+/\\d+");
            if (!match.Success)
                return;

            string updated = $"{ui.currentPerkCount}/{ui.maxPerkCount}";
            slotCounter.text = text.Substring(0, match.Index) + updated + text.Substring(match.Index + match.Length);
        }

        internal static void ApplyCustomPerkElement(StartingPerkElement element, CustomStartProfile profile)
        {
            if (element == null || profile == null)
                return;

            element.perk = GetOrCreate(profile);

            Sprite sprite = PerkIconLoader.Get(profile);
            if (sprite != null && element.icon != null)
                element.icon.sprite = sprite;
        }

        internal static void EnsureRegistered()
        {
            Il2CppSystem.Collections.Generic.List<StartingPerk> perks = StartingPerkList.Perks;
            if (perks == null)
                return;

            foreach (CustomStartProfile profile in CustomStartPerkRegistry.All)
            {
                if (!Contains(perks, profile.Id))
                    perks.Add(GetOrCreate(profile));
            }
        }

        internal static void EnsurePicker(PerkUIController ui)
        {
            if (ui == null || ui.availablePerks == null || ui.perkElementPrefab == null)
                return;

            EnsureRegistered();
            int startType = StartTypeResolver.Resolve();
            bool added = false;

            foreach (CustomStartProfile profile in CustomStartPerkRegistry.All)
            {
                bool visible = StartTypeResolver.IsVisibleForStartType(profile, startType);
                StartingPerkElement element = FindElement(ui.availablePerks, profile.Id);

                if (visible)
                {
                    if (element == null)
                    {
                        GameObject obj = UnityEngine.Object.Instantiate(ui.perkElementPrefab, ui.availablePerks.transform);
                        element = obj.GetComponent<StartingPerkElement>();
                        if (element == null)
                        {
                            UnityEngine.Object.Destroy(obj);
                            continue;
                        }
                        element.id = profile.Id;
                        element.isSelected = false;
                        ApplyCustomPerkElement(element, profile);
                        obj.SetActive(true);
                        added = true;
                        continue;
                    }

                    element.gameObject.SetActive(true);
                    ApplyCustomPerkElement(element, profile);
                    continue;
                }

                if (element != null)
                    element.gameObject.SetActive(false);
                DeselectCustomPerk(ui, profile.Id);
            }

            if (added)
                ui.SortPerkContainer(ui.availablePerks);
        }

        private static void DeselectCustomPerk(PerkUIController ui, string id)
        {
            if (ui?.selectedPerks == null || string.IsNullOrEmpty(id))
                return;

            StartingPerkElement selected = FindElement(ui.selectedPerks, id);
            if (selected == null)
                return;

            try
            {
                ui.DeselectPerk(selected);
            }
            catch
            {
                selected.isSelected = false;
            }
        }

        private static StartingPerk GetOrCreate(CustomStartProfile profile)
        {
            if (Created.TryGetValue(profile.Id, out StartingPerk existing) && existing != null)
            {
                existing.cost = profile.Cost;
                existing.type = (StartingPerk.StartingPerkType)profile.Type;
                existing.rawName = profile.Name?.Pick() ?? profile.Id;
                existing.rawDescription = profile.Description?.Pick() ?? "";
                return existing;
            }

            StartingPerk perk = new StartingPerk
            {
                id = profile.Id,
                cost = profile.Cost,
                maxSlot = 0,
                type = (StartingPerk.StartingPerkType)profile.Type,
                rawName = profile.Name?.Pick() ?? profile.Id,
                rawDescription = profile.Description?.Pick() ?? "",
                incompatiblePerks = new Il2CppSystem.Collections.Generic.List<string>()
            };
            Created[profile.Id] = perk;
            return perk;
        }

        private static bool Contains(Il2CppSystem.Collections.Generic.List<StartingPerk> list, string id)
        {
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] != null && string.Equals(list[i].id, id, StringComparison.Ordinal))
                    return true;
            }
            return false;
        }

        private static StartingPerkElement FindElement(GameObject root, string id)
        {
            foreach (StartingPerkElement element in root.GetComponentsInChildren<StartingPerkElement>(true))
            {
                if (element != null && string.Equals(element.id, id, StringComparison.Ordinal))
                    return element;
            }
            return null;
        }
    }
}
