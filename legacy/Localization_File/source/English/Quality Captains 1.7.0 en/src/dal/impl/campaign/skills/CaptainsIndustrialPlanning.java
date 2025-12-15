package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.campaign.econ.MarketAPI;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.characters.MarketSkillEffect;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

public class CaptainsIndustrialPlanning {
	
	public static int SUPPLY_BONUS = 1;
	public static float ACCESS_BONUS = 25f;
	public static float CUSTOM_PRODUCTION_BONUS = 50f;
	public static int SHIP_QUAL_BONUS = 10;
	
	public static class Level1 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			stats.getDynamic().getMod(Stats.SUPPLY_BONUS_MOD).modifyFlat(id, SUPPLY_BONUS);
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.SUPPLY_BONUS_MOD).unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + SUPPLY_BONUS + " 所有工业设施的全部产品的产量";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.GOVERNED_OUTPOST;
		}
	}
	
	public static class Level1B implements MarketSkillEffect {
		public void apply(MarketAPI market, String id, float level) {
			market.getAccessibilityMod().modifyFlat(id, (ACCESS_BONUS * 0.01f), "工业计划");
		}

		public void unapply(MarketAPI market, String id) {
			market.getAccessibilityMod().unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(ACCESS_BONUS) + "% 流通性";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.GOVERNED_OUTPOST;
		}
	}
	
	public static class Level2 extends BaseSkillEffectDescription implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			//stats.getDynamic().getMod(Stats.CUSTOM_PRODUCTION_MOD).modifyPercent(id, CUSTOM_PRODUCTION_BONUS, "工业计划");
			stats.getDynamic().getMod(Stats.CUSTOM_PRODUCTION_MOD).modifyMult(id, 1f + CUSTOM_PRODUCTION_BONUS/100f, "工业计划");
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			//stats.getDynamic().getMod(Stats.CUSTOM_PRODUCTION_MOD).unmodifyPercent(id);
			stats.getDynamic().getMod(Stats.CUSTOM_PRODUCTION_MOD).unmodifyMult(id);
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
											TooltipMakerAPI info, float width) {
			init(stats, skill);
			float opad = 10f;
			Color c = Misc.getBasePlayerColor();
			info.addPara("影响: %s", opad + 5f, Misc.getGrayColor(), c, "所有殖民地");
			info.addSpacer(opad);
			info.addPara("+%s 每个月生产舰船与武器时的最大产能", 0f, hc, hc,
					"" + (int) CUSTOM_PRODUCTION_BONUS + "%");
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_OUTPOSTS;
		}
	}
	
	public static class Level3 implements CharacterStatsSkillEffect {
		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			//stats.getDynamic().getMod(Stats.CUSTOM_PRODUCTION_MOD).modifyPercent(id, CUSTOM_PRODUCTION_BONUS, "工业计划");
			stats.getDynamic().getMod(Stats.FLEET_QUALITY_MOD).modifyMult(id, 1f + SHIP_QUAL_BONUS/100f, "工业计划");
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			stats.getDynamic().getMod(Stats.FLEET_QUALITY_MOD).unmodifyMult(id);
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.GOVERNED_OUTPOST;
		}

		public String getEffectDescription(float level) {
			return "+" + SHIP_QUAL_BONUS + "% 所有生成舰队的舰船质量";
		}

		public String getEffectPerLevelDescription() {
			return null;
		}
	}	
}


