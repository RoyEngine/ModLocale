package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.FleetStatsSkillEffect;
import com.fs.starfarer.api.fleet.MutableFleetStatsAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;

public class CaptainsSensors {
	
	public static float DETECTED_BONUS = 25f;
	public static float SENSOR_BONUS = 50f;
	
	public static float SLOW_BURN_BONUS = 3f;
	
	public static float GO_DARK_MULT = 0.8f;

	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			//int base = (int) RingSystemTerrainPlugin.MAX_SNEAK_BURN_LEVEL;
//			return "*A slow-moving fleet is harder to detect in some types of terrain, and can avoid some hazards. " +
//				"Several abilities also make the fleet move slowly when they are activated. The base burn " +
//				"level at which a fleet is considered to be slow-moving is " + base + ".";			
			//int reduction = (int)Math.round((1f - Misc.SNEAK_BURN_MULT) * 100f);
			return "*缓速航行的舰队在某些地形中更难被发现，并且可以避免某些危险。有些能力能够减慢舰队的航行速度。当舰队的移动速度为舰队中最慢的舰船的 最大宇宙航速 的一半时，该舰队视作缓速航行。";			
		}
		public Color[] getHighlightColors() {
			return null;
//			Color h = Misc.getHighlightColor();
//			h = Misc.getDarkHighlightColor();
//			return new Color[] {h};
		}
		public String[] getHighlights() {
			return null;
//			int base = (int) RingSystemTerrainPlugin.MAX_SNEAK_BURN_LEVEL;
//			return new String [] {"" + base};
		}
		public Color getTextColor() {
			return null;
		}
	}
	
	public static class Level1 implements FleetStatsSkillEffect {
		public void apply(MutableFleetStatsAPI stats, String id, float level) {
			stats.getDetectedRangeMod().modifyMult(id, 1f - DETECTED_BONUS / 100f, "传感探测 技能");
		}
		
		public void unapply(MutableFleetStatsAPI stats, String id) {
			stats.getDetectedRangeMod().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int) DETECTED_BONUS + "% 被侦测范围";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level2 implements FleetStatsSkillEffect {
		public void apply(MutableFleetStatsAPI stats, String id, float level) {
			stats.getSensorRangeMod().modifyPercent(id, SENSOR_BONUS, "传感探测 技能");
		}
		
		public void unapply(MutableFleetStatsAPI stats, String id) {
			stats.getSensorRangeMod().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int) SENSOR_BONUS + "% 传感器探测范围";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level3 implements FleetStatsSkillEffect {
		public void apply(MutableFleetStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat(id, SLOW_BURN_BONUS);
		}
		
		public void unapply(MutableFleetStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int) SLOW_BURN_BONUS + " 当舰队处于 缓速航行* 时的最大宇宙航行速度*";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level2B implements FleetStatsSkillEffect {
		public void apply(MutableFleetStatsAPI stats, String id, float level) {
			stats.getDynamic().getStat(Stats.GO_DARK_DETECTED_AT_MULT).modifyMult(id, GO_DARK_MULT);
		}
		
		public void unapply(MutableFleetStatsAPI stats, String id) {
			stats.getDynamic().getStat(Stats.GO_DARK_DETECTED_AT_MULT).unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "在使用 \"匿踪\" 能力时，你的舰队的被探测范围降低至 " + (GO_DARK_MULT * 100f) + "%";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
}



