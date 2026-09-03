using System;
using System.Collections.Generic;
using HarmonyLib;
using Il2Cpp;
using Il2CppSystem.Collections.Generic;
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
    internal static class PerkElementIconPatch
    {
        private static void Postfix(StartingPerkElement __instance)
        {
            CustomStartProfile profile = CustomStartPerkRegistry.Find(__instance?.id);
            if (profile == null || __instance.icon == null)
                return;
            Sprite sprite = PerkIconLoader.Get(profile);
            if (sprite != null)
                __instance.icon.sprite = sprite;
        }
    }

    internal static class CustomStartPerkUi
    {
        private static readonly Dictionary<string, StartingPerk> Created =
            new Dictionary<string, StartingPerk>(StringComparer.Ordinal);

        internal static void EnsureRegistered()
        {
            List<StartingPerk> perks = StartingPerkList.Perks;
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
            int startType = ResolveCurrentStartType();
            bool added = false;

            foreach (CustomStartProfile profile in CustomStartPerkRegistry.All)
            {
                if (!profile.AllowsStartType(startType))
                    continue;

                StartingPerkElement element = FindElement(ui.availablePerks, profile.Id);
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
                    obj.SetActive(true);
                    added = true;
                }

                element.perk = GetOrCreate(profile);
                Sprite sprite = PerkIconLoader.Get(profile);
                if (sprite != null && element.icon != null)
                    element.icon.sprite = sprite;
            }

            if (added)
                ui.SortPerkContainer(ui.availablePerks);
        }

        private static StartingPerk GetOrCreate(CustomStartProfile profile)
        {
            if (Created.TryGetValue(profile.Id, out StartingPerk existing) && existing != null)
            {
                existing.cost = profile.Cost;
                existing.type = (StartingPerkType)profile.Type;
                return existing;
            }

            StartingPerk perk = new StartingPerk
            {
                id = profile.Id,
                cost = profile.Cost,
                maxSlot = 0,
                type = (StartingPerkType)profile.Type,
                rawName = profile.Name?.Pick() ?? profile.Id,
                rawDescription = profile.Description?.Pick() ?? "",
                incompatiblePerks = new List<string>()
            };
            Created[profile.Id] = perk;
            return perk;
        }

        private static int ResolveCurrentStartType()
        {
            try
            {
                NewGameData data = NewGameData.Instance;
                if (data != null)
                    return (int)data.startType;
            }
            catch
            {
                // ignored
            }
            return CustomStartFrameworkPlugin.PendingStartType;
        }

        private static bool Contains(List<StartingPerk> list, string id)
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
