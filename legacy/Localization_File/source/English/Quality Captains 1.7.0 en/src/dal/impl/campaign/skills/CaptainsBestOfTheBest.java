package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.util.Misc;

public class CaptainsBestOfTheBest {

	public static int EXTRA_LMODS = 1;
	public static int EXTRA_SMODS = 1;
	public static float DEPLOYMENT_BONUS = 10f;
	public static float CPR_BONUS = 100;
	

	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			int max = Global.getSettings().getInt("maxPermanentHullmods");
			int maxL = Global.getSettings().getInt("maxLogisticsHullmods");
			return "*舰船基础可内置的船插的上限为 " +
					max + "。\n**舰船基础可内置的后勤船插的上限为 " + maxL + "。"
					;
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			return new Color[] {h, h, h};
		}
		public String[] getHighlights() {
			int max = Global.getSettings().getInt("maxPermanentHullmods");
			int maxL = Global.getSettings().getInt("maxLogisticsHullmods");
			return new String [] {"" + max, "" + maxL};
		}
		public Color getTextColor() {
			return null;
		}
	}
	
	
	public static class Level1 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getDynamic().getMod(Stats.MAX_PERMANENT_HULLMODS_MOD).modifyFlat(id, EXTRA_SMODS);
			stats.getDynamic().getMod(Stats.MAX_LOGISTICS_HULLMODS_MOD).modifyFlat(id, EXTRA_SMODS);
		}

		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.MAX_PERMANENT_HULLMODS_MOD).unmodifyFlat(id);
			stats.getDynamic().getMod(Stats.MAX_LOGISTICS_HULLMODS_MOD).unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			return "增加" + EXTRA_SMODS + " 个最大可 内置* 舰船插件数，增加 " + EXTRA_LMODS + " 个最大可内置后勤船插**数";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level2 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD).modifyFlat(id, (DEPLOYMENT_BONUS / 100f));
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD).unmodifyFlat(id);
		}

		public String getEffectDescription(float level) {
//			return "Deployment points increased as if holding an objective worth " + 
//						(int)Math.round(DEPLOYMENT_BONUS * 100f) + "% of the battle size (equivalent to a Comm Relay)";
			return "即使未占领任何目标点，仍能给予当前战斗规模  " + 
			(int)Math.round(DEPLOYMENT_BONUS) + "% 的部署点奖励";
		}

		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_SHIPS;
		}
	}
	
	//Modified from SupportDoctrine
	public static class Level3 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.COMMAND_POINT_RATE_FLAT).modifyFlat(id, CPR_BONUS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.COMMAND_POINT_RATE_FLAT).unmodifyFlat(id);
		}

		public String getEffectDescription(float level) {

			return "+" + (int)CPR_BONUS + "% 指挥点恢复速度";
		}

		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
}





