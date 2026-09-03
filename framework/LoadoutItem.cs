using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CustomStartFramework
{
    public enum WaterKind
    {
        Pure,
        HighQuality,
        Base,
        Ghost,
        Rust,
        Gutterflow,
        Nutrient
    }

    public static class WaterTypeParser
    {
        public static bool TryParse(string raw, out WaterKind kind)
        {
            kind = default;
            if (string.IsNullOrWhiteSpace(raw)) return false;
            string key = raw.Trim().ToLowerInvariant()
                .Replace('-', '_')
                .Replace(' ', '_');
            switch (key)
            {
                case "pure":
                case "pure_water":
                case "purewater":
                    kind = WaterKind.Pure;
                    return true;
                case "high_quality":
                case "highquality":
                case "hq":
                case "high":
                case "premium":
                    kind = WaterKind.HighQuality;
                    return true;
                case "base":
                case "basewater":
                case "base_water":
                    kind = WaterKind.Base;
                    return true;
                case "ghost":
                case "ghostwater":
                case "ghost_water":
                    kind = WaterKind.Ghost;
                    return true;
                case "rust":
                case "rustwater":
                case "rust_water":
                    kind = WaterKind.Rust;
                    return true;
                case "gutterflow":
                case "gutter":
                case "gutter_flow":
                    kind = WaterKind.Gutterflow;
                    return true;
                case "nutrient":
                case "nutrient_solution":
                case "nutrients":
                    kind = WaterKind.Nutrient;
                    return true;
                default:
                    return false;
            }
        }
    }

    [JsonConverter(typeof(LoadoutItemConverter))]
    public class LoadoutItem
    {
        public string Id { get; set; }
        public int? Charge { get; set; }
        public string Water { get; set; }
        public int? VolumeMl { get; set; }
    }

    public sealed class LoadoutItemConverter : JsonConverter<LoadoutItem>
    {
        public override LoadoutItem Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            if (reader.TokenType == JsonTokenType.String)
                return new LoadoutItem { Id = reader.GetString() };

            if (reader.TokenType == JsonTokenType.Null)
                return null;

            if (reader.TokenType != JsonTokenType.StartObject)
                throw new JsonException($"Item entry must be a string or object, got {reader.TokenType}.");

            using JsonDocument doc = JsonDocument.ParseValue(ref reader);
            JsonElement root = doc.RootElement;
            var item = new LoadoutItem();
            foreach (JsonProperty prop in root.EnumerateObject())
            {
                switch (prop.Name.ToLowerInvariant())
                {
                    case "id":
                        item.Id = prop.Value.ValueKind == JsonValueKind.String ? prop.Value.GetString() : prop.Value.ToString();
                        break;
                    case "charge":
                        item.Charge = ReadInt(prop.Value, "charge");
                        break;
                    case "water":
                        item.Water = prop.Value.ValueKind == JsonValueKind.Null ? null : prop.Value.GetString();
                        break;
                    case "volumeml":
                        item.VolumeMl = ReadInt(prop.Value, "volumeMl");
                        break;
                }
            }
            return item;
        }

        public override void Write(Utf8JsonWriter writer, LoadoutItem value, JsonSerializerOptions options)
        {
            if (value == null)
            {
                writer.WriteNullValue();
                return;
            }
            bool simple = value.Charge == null && string.IsNullOrEmpty(value.Water) && value.VolumeMl == null;
            if (simple)
            {
                writer.WriteStringValue(value.Id ?? "");
                return;
            }
            writer.WriteStartObject();
            writer.WriteString("id", value.Id ?? "");
            if (value.Charge.HasValue) writer.WriteNumber("charge", value.Charge.Value);
            if (!string.IsNullOrEmpty(value.Water)) writer.WriteString("water", value.Water);
            if (value.VolumeMl.HasValue) writer.WriteNumber("volumeMl", value.VolumeMl.Value);
            writer.WriteEndObject();
        }

        private static int? ReadInt(JsonElement el, string field)
        {
            if (el.ValueKind == JsonValueKind.Null) return null;
            if (el.ValueKind == JsonValueKind.Number)
            {
                if (el.TryGetInt32(out int i)) return i;
                if (el.TryGetDouble(out double d)) return (int)d;
            }
            if (el.ValueKind == JsonValueKind.String && int.TryParse(el.GetString(), out int parsed))
                return parsed;
            throw new JsonException($"Field '{field}' must be an integer.");
        }
    }

    internal static class FactionDefaults
    {
        public static Dictionary<string, int> CreateReputationDelta() =>
            new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase)
            {
                ["lower"] = 0,
                ["upper"] = 0,
                ["security"] = 0,
                ["black_market"] = 0,
                ["revolution"] = 0,
                ["cartel"] = 0,
            };
    }
}
