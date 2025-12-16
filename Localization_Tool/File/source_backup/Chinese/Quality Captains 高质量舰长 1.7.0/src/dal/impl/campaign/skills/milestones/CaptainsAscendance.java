package dal.impl.campaign.skills.milestones;

import java.io.IOException;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.FleetDataAPI;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.FleetTotalItem;
import com.fs.starfarer.api.characters.FleetTotalSource;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.characters.LevelBasedEffect.ScopeDescription;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI.SkillLevelAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.impl.campaign.ids.HullMods;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.loading.HullModSpecAPI;
import com.fs.starfarer.api.ui.TooltipMakerAPI;

public class CaptainsAscendance { //Sentinel
	
	public static float MAG = 1f;
	
	public static boolean enabled = false;
	public static final String skillID = "captains_ascendance";
	public static final String skillName = "飞升";
	public static final String skillDesc = "让我飞向月球，让我在星空中嬉戏。让我看看……木星和火星上的春天是何等模样。";
	public static final String skillAuthor = "古人类艺术家";
	public static final String skillIcon = "/graphics/icons/skills/"+ skillID + ".png";
	
	public static class Level1 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getDynamic().getMod(Stats.COORDINATED_MANEUVERS_FLAT).modifyFlat(id, MAG);
		}
			
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.COORDINATED_MANEUVERS_FLAT).unmodifyFlat(id);
		}

		public String getEffectDescription(float level) {
			if (enabled) return "你部署的每艘舰船，提升 " + Math.round(MAG) + " 舰队导航效率";
			return "";
		}
			
		public ScopeDescription getScopeDescription() {
			if (enabled) return ScopeDescription.ALL_SHIPS;
			return ScopeDescription.NONE;
		}

		public String getEffectPerLevelDescription() {
			return null;
		}
	}

	public static void toggleMilestone() {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId().equals(skillID)) {
				if (skill.getLevel()==0) {
					skill.getSkill().setDescription(skillDesc);
					skill.getSkill().setAuthor(skillAuthor);
					skill.getSkill().setName(skillName);
					try {
						Global.getSettings().loadTexture(skillIcon);
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName(skillIcon);
					//skill.getSkill().getTags().remove("npc_only");
					skill.getSkill().setPermanent(true);
					skill.setLevel(1);
					enabled = true;
				} else {
					skill.getSkill().setDescription("发挥你的全部潜能。");
					skill.getSkill().setAuthor("");
					skill.getSkill().setName("未来里程碑");
					try {
						Global.getSettings().loadTexture("graphics/icons/skills/blank.png");
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName("graphics/icons/skills/blank.png");				
					//skill.getSkill().addTag("npc_only");
					skill.getSkill().setPermanent(false);
					skill.setLevel(0);
					enabled = false;
				}
			}
		}
	}
	
	public static void enableDisable() {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId().equals(skillID)) {
				if (skill.getLevel() > 0) {
					skill.getSkill().setDescription(skillDesc);
					skill.getSkill().setAuthor(skillAuthor);
					skill.getSkill().setName(skillName);
					try {
						Global.getSettings().loadTexture(skillIcon);
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName(skillIcon);
					skill.getSkill().setPermanent(true);
					enabled = true;
				} else {
					skill.getSkill().setDescription("发挥你的全部潜能。");
					skill.getSkill().setAuthor("");
					skill.getSkill().setName("未来里程碑");
					try {
						Global.getSettings().loadTexture("graphics/icons/skills/blank.png");
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName("graphics/icons/skills/blank.png");				
					skill.getSkill().setPermanent(false);
					enabled = false;
				}
			}
		}
	}
}





