package second_in_command.skills.smallcraft

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.CoordinatedManeuversScript
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class CoordinatedManeuvers : SCBaseSkillPlugin() {

    var max = CoordinatedManeuversScript.BASE_MAXIMUM.toInt()

    override fun getAffectsString(): String {
        return "所有指派有军官的舰船，包括旗舰"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {
        tooltip.addPara("增加部署舰船的 导航效率*", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - +6%% 每艘护卫舰",0f, Misc.getTextColor(), Misc.getHighlightColor(), "+6%")
        tooltip.addPara("   - +3%% 每艘驱逐舰",0f, Misc.getTextColor(), Misc.getHighlightColor(), "+3%")
        tooltip.addPara("   - +1%% 每艘更大舰船",0f, Misc.getTextColor(), Misc.getHighlightColor(), "+1%")

        tooltip.addSpacer(10f)

        tooltip.addPara("+50%% 指挥点回复速度 (每部署 1 艘护卫舰)，驱逐舰则 +25%%", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)


        tooltip.addPara("*舰队导航效率能提高已部署舰船的最高航速，" +
	"最高能提高 $max%%}。但对战机无效。", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "$max%")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        var officer = stats?.fleetMember?.captain ?: return
        if (officer.isDefault) return

        var navBonus = 0f
        navBonus = when (hullSize) {
            ShipAPI.HullSize.FRIGATE -> 6f
            ShipAPI.HullSize.DESTROYER -> 3f
            else -> 1f
        }

        stats.dynamic.getMod(Stats.COORDINATED_MANEUVERS_FLAT).modifyFlat(id, navBonus)

        var commandBonus = 0f

        commandBonus = when (hullSize) {
            ShipAPI.HullSize.FRIGATE -> 50f
            ShipAPI.HullSize.DESTROYER -> 25f
            else -> 0f
        }

        stats.dynamic.getMod(Stats.COMMAND_POINT_RATE_FLAT).modifyFlat(id, commandBonus * 0.01f)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

}