package dal.impl.campaign.skills;

import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.FleetStatsSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.fleet.MutableFleetStatsAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;

public class CaptainsFieldRepairs {
	
	public static float REPAIR_RATE_BONUS = 100f;
	public static float INSTA_REPAIR_PERCENT = 30f; //50
	public static float DMOD_REDUCTION = 2f;
	public static float MAINTENANCE_COST_REDUCTION = 20;
	
	public static class Level1 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getRepairRateMult().modifyPercent(id, REPAIR_RATE_BONUS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getRepairRateMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "" + (int) REPAIR_RATE_BONUS + "% 战后舰船修理速度";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_SHIPS;
		}
	}
	
	public static class Level2 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getDynamic().getMod(Stats.INSTA_REPAIR_FRACTION).modifyFlat(id, (float)INSTA_REPAIR_PERCENT / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.INSTA_REPAIR_FRACTION).unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "" + (int) Math.round(INSTA_REPAIR_PERCENT) + "% 的结构和装甲损伤将在战后自动修复，且不消耗补给";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_SHIPS;
		}
	}
	
	public static class Level3 implements FleetStatsSkillEffect {
		public void apply(MutableFleetStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.SHIP_DMOD_REDUCTION).modifyFlat(id, DMOD_REDUCTION);	
		}
		
		public void unapply(MutableFleetStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.SHIP_DMOD_REDUCTION).unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			//return "Recovered non-friendly ships have an average of " + (int) DMOD_REDUCTION + " less subsystem with lasting damage";
			//return "Recovered ships have up to " + (int) DMOD_REDUCTION + " less d-mods";
			return "降低修复打捞舰船时出现  D-插件 的概率";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level4 implements FleetStatsSkillEffect {
		public void apply(MutableFleetStatsAPI stats, String id, float level) {
		}
		
		public void unapply(MutableFleetStatsAPI stats, String id) {
		}
		
		public String getEffectDescription(float level) {
			if (CaptainsFieldRepairsScript.MONTHS_PER_DMOD_REMOVAL == 1) {
				return "每一个月，就有几率从随机一艘船上移除一个 D-插件";
			} else if (CaptainsFieldRepairsScript.MONTHS_PER_DMOD_REMOVAL == 2) {
				return "每两个月，就有几率从随机一艘船上移除一个 D-插件";
			} else {
				return "每 " +
							//CaptainsFieldRepairsScript.MONTHS_PER_DMOD_REMOVAL + " months";
							" 个月，就有几率从随机一艘船上移除一个 D-插件，\n取决于其大小和复杂性。";
			}
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level5 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getSuppliesPerMonth().modifyMult(id, 1f - ((float)(MAINTENANCE_COST_REDUCTION)/100f), "舰队后勤 技能");
		}

		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getSuppliesPerMonth().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + Math.round(MAINTENANCE_COST_REDUCTION) + "% 维护成本";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_SHIPS;
		}
	}
}
